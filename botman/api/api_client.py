import aiohttp
import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        
    async def get_guild_prefix(self, guild_id: str) -> str:
        """Get custom prefix for a guild."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/guilds/{guild_id}/prefix") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data["prefix"]
                    return "!"  # Default prefix on failure
            except Exception as e:
                logger.error(f"Failed to get guild prefix: {e}")
                return "!"

    async def set_guild_prefix(self, guild_id: str, prefix: str) -> bool:
        """Set custom prefix for a guild."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.put(
                    f"{self.base_url}/guilds/{guild_id}/prefix",
                    json={"prefix": prefix}
                ) as resp:
                    return resp.status == 200
            except Exception as e:
                logger.error(f"Failed to set guild prefix: {e}")
                return False

    async def store_deleted_message(self, message_data: Dict) -> bool:
        """Store a deleted message."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.base_url}/messages/deleted",
                    json=message_data
                ) as resp:
                    return resp.status == 201
            except Exception as e:
                logger.error(f"Failed to store deleted message: {e}")
                return False

    async def store_edited_message(self, message_data: Dict) -> bool:
        """Store an edited message."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.base_url}/messages/edited",
                    json=message_data
                ) as resp:
                    return resp.status == 201
            except Exception as e:
                logger.error(f"Failed to store edited message: {e}")
                return False

    async def get_recent_deleted_messages(self, guild_id: str) -> List[Dict]:
        """Get recent deleted messages for a guild."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/guilds/{guild_id}/messages/deleted") as resp:
                    if resp.status == 200:
                        return await resp.json()
                    return []
            except Exception as e:
                logger.error(f"Failed to get deleted messages: {e}")
                return []

    async def get_recent_edited_messages(self, guild_id: str) -> List[Dict]:
        """Get recent edited messages for a guild."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/guilds/{guild_id}/messages/edited") as resp:
                    if resp.status == 200:
                        return await resp.json()
                    return []
            except Exception as e:
                logger.error(f"Failed to get edited messages: {e}")
                return []