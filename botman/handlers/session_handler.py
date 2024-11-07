from __future__ import annotations

import asyncio
import typing
import random
from datetime import datetime, timedelta

import hikari

from ongaku import errors
from ongaku.abc import handler as handler_
from ongaku.abc import session as session_
from ongaku.internal import logger

if typing.TYPE_CHECKING:
    from ongaku.client import Client
    from ongaku.player import Player
    from ongaku.session import Session

class RetrySessionHandler(handler_.SessionHandler):
    """
    Session Handler with retry capabilities.
    
    This handler extends the basic functionality by adding retry mechanisms when sessions
    fail or become unavailable. It implements exponential backoff with jitter for retries
    and keeps track of session health.
    """

    __slots__: typing.Sequence[str] = (
        "_client",
        "_is_alive",
        "_current_session",
        "_sessions",
        "_players",
        "_retry_attempts",
        "_last_retry",
        "_max_retries",
        "_base_delay",
    )

    def __init__(
        self,
        client: Client,
        max_retries: int = 5,
        base_delay: float = 2.0
    ) -> None:
        self._client = client
        self._is_alive = False
        self._current_session: Session | None = None
        self._sessions: typing.MutableMapping[str, Session] = {}
        self._players: typing.MutableMapping[hikari.Snowflake, Player] = {}
        
        # Retry-specific attributes
        self._retry_attempts: typing.MutableMapping[str, int] = {}
        self._last_retry: typing.MutableMapping[str, datetime] = {}
        self._max_retries = max_retries
        self._base_delay = base_delay

    @property
    def sessions(self) -> typing.Sequence[Session]:
        """The sessions attached to this handler."""
        return tuple(self._sessions.values())

    @property
    def players(self) -> typing.Sequence[Player]:
        """The players attached to this handler."""
        return tuple(self._players.values())

    @property
    def is_alive(self) -> bool:
        """Whether the handler is alive or not."""
        return self._is_alive

    async def _attempt_reconnect(self, session: Session) -> bool:
        """
        Attempts to reconnect a session using exponential backoff with jitter.
        
        Returns:
            bool: True if reconnection was successful, False otherwise.
        """
        session_name = session.name
        current_attempts = self._retry_attempts.get(session_name, 0)
        
        if current_attempts >= self._max_retries:
            return False
            
        # Calculate delay with exponential backoff and jitter
        delay = self._base_delay * (2 ** current_attempts)
        jitter = random.uniform(0, 0.1 * delay)
        total_delay = delay + jitter
        
        # Update retry tracking
        self._retry_attempts[session_name] = current_attempts + 1
        self._last_retry[session_name] = datetime.now()
        
        try:
            await asyncio.sleep(total_delay)
            await session.start()
            # Reset retry attempts on successful connection
            self._retry_attempts[session_name] = 0
            return True
        except Exception as e:
            logger.logger.error(f"Retry attempt {current_attempts + 1} failed for session {session_name}: {e}")
            return False

    async def retry_session(self, name: str) -> Session:
        """
        Attempts to retry connecting to a specific session.
        
        Args:
            name: The name of the session to retry.
            
        Returns:
            Session: The successfully reconnected session.
            
        Raises:
            errors.SessionMissingError: If the session doesn't exist.
            errors.SessionRetryError: If all retry attempts fail.
        """
        try:
            session = self._sessions[name]
        except KeyError:
            raise errors.SessionMissingError
            
        if await self._attempt_reconnect(session):
            return session
            
        raise errors.SessionRetryError(f"Failed to reconnect session {name} after {self._max_retries} attempts")

    async def start(self) -> None:
        self._is_alive = True

        for session in self.sessions:
            if session.status == session_.SessionStatus.NOT_CONNECTED:
                try:
                    await session.start()
                    logger.logger.info(f"Successfully started session {session.name}")
                except Exception as e:
                    logger.logger.error(f"Failed to start session {session.name}: {e}")
                    await self.retry_session(session.name)

    async def stop(self) -> None:
        for session in self.sessions:
            await session.stop()

        self._players.clear()
        self._retry_attempts.clear()
        self._last_retry.clear()
        self._is_alive = False

    def add_session(self, session: Session) -> Session:
        """Add a session."""
        if self.is_alive:
            asyncio.create_task(session.start())

        if self._sessions.get(session.name, None) is None:
            self._sessions.update({session.name: session})
            return session

        raise errors.UniqueError(f"The name {session.name} is not unique.")

    def fetch_session(self, name: str | None = None) -> Session:
        """
        Fetch a session, attempting to retry if it's disconnected.
        """
        if name is not None:
            try:
                session = self._sessions[name]
                if session.status != session_.SessionStatus.CONNECTED:
                    asyncio.create_task(self.retry_session(name))
                return session
            except KeyError:
                raise errors.SessionMissingError

        if self._current_session and self._current_session.status == session_.SessionStatus.CONNECTED:
            return self._current_session

        # Try to find a connected session
        for session in self.sessions:
            if session.status == session_.SessionStatus.CONNECTED:
                self._current_session = session
                return session

        # If no connected sessions found, try to retry the first available session
        if self.sessions:
            first_session = self.sessions[0]
            asyncio.create_task(self.retry_session(first_session.name))
            return first_session

        raise errors.NoSessionsError

    async def delete_session(self, name: str) -> None:
        try:
            session = self._sessions.pop(name)
            self._retry_attempts.pop(name, None)
            self._last_retry.pop(name, None)
        except KeyError:
            raise errors.SessionMissingError

        await session.stop()

    def add_player(self, player: Player) -> Player:
        if self._players.get(player.guild_id, None) is not None:
            raise errors.UniqueError(
                f"A player with the guild id {player.guild_id} has already been made."
            )

        self._players.update({player.guild_id: player})
        return player

    def fetch_player(self, guild: hikari.SnowflakeishOr[hikari.Guild]) -> Player:
        player = self._players.get(hikari.Snowflake(guild))

        if player:
            return player

        raise errors.PlayerMissingError

    async def delete_player(self, guild: hikari.SnowflakeishOr[hikari.Guild]) -> None:
        try:
            player = self._players.pop(hikari.Snowflake(guild))
        except KeyError:
            raise errors.PlayerMissingError

        await player.disconnect()