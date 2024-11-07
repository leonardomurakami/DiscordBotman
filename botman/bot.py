import logging
import hikari
import lightbulb
import miru
import ongaku

from help import HelpCommand
from config import BotConfig, LavalinkConfig, LogConfig
from handlers.session_handler import RetrySessionHandler
from handlers.error_handler import ErrorHandler
from handlers.message_handler import MessageHandler

logger = logging.getLogger(__name__)


class Bot(lightbulb.BotApp):
    """Main bot class with all core functionality."""
    
    def __init__(self):
        # Load configurations
        self.config = BotConfig()
        self.lavalink_config = LavalinkConfig()
        self.log_config = LogConfig()
        
        # Initialize the bot
        super().__init__(
            token=self.config.token,
            prefix=self.config.prefix,
            help_class=HelpCommand,
            intents=hikari.Intents.ALL,
            owner_ids=self.config.owner_ids
        )
        
        # Initialize storage
        self.d.deleted_messages = {}
        self.d.edited_messages = {}
        
        # Initialize handlers
        self.message_handler = MessageHandler(self)
        self.error_handler = ErrorHandler()
        
        # Setup components
        self._setup_logging()
        self._setup_integrations()
        self._load_extensions()
        self._register_events()

    def _setup_logging(self) -> None:
        """Configure logging settings."""
        logging.basicConfig(
            level=getattr(logging, self.log_config.level),
            format=self.log_config.format,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(self.log_config.file_path)
            ]
        )
        logger.info("Logging system initialized")

    def _setup_integrations(self) -> None:
        """Initialize third-party integrations."""
        # Setup Miru for components
        self.d.miru = miru.Client(self)
        
        # Setup Ongaku for music
        self.d.ongaku = ongaku.Client(self, session_handler=RetrySessionHandler)
        self.d.ongaku.create_session(
            name="default-session",
            host=self.lavalink_config.host,
            port=self.lavalink_config.port,
            password=self.lavalink_config.password,
        )
        logger.info("Third-party integrations initialized")

    def _load_extensions(self) -> None:
        """Load all command extensions."""
        try:
            self.load_extensions_from("./plugins", recursive=True)
            logger.info("Command extensions loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load extensions: {e}")
            raise

    def _register_events(self) -> None:
        """Register event handlers."""
        self.listen(hikari.StartedEvent)(self.on_started)
        self.listen(lightbulb.CommandErrorEvent)(self.on_error)
        self.listen(hikari.GuildMessageDeleteEvent)(self.message_handler.on_message_delete)
        self.listen(hikari.GuildMessageUpdateEvent)(self.message_handler.on_message_edit)
        logger.info("Event handlers registered")

    async def on_started(self, event: hikari.StartedEvent) -> None:
        """Handler for bot startup."""
        logger.info("Bot has started successfully!")

    async def on_error(self, event: lightbulb.CommandErrorEvent) -> None:
        """Central error handler that delegates to specific handlers."""
        try:
            if isinstance(event.exception, lightbulb.CommandNotFound):
                await self.error_handler.handle_command_not_found(event)
            elif isinstance(event.exception, lightbulb.MissingRequiredPermission):
                await self.error_handler.handle_missing_permissions(event)
            elif isinstance(event.exception, lightbulb.NotOwner):
                await self.error_handler.handle_not_owner(event)
            elif isinstance(event.exception, lightbulb.CommandIsOnCooldown):
                await self.error_handler.handle_cooldown(event)
            elif isinstance(event.exception, lightbulb.NotEnoughArguments):
                await self.error_handler.handle_missing_arguments(event)
            elif isinstance(event.exception, lightbulb.CommandInvocationError):
                await self.error_handler.handle_command_invocation_error(event)
            else:
                await self.error_handler.handle_unexpected_error(event)
        except Exception as e:
            logger.error(f"Error in error handler: {e}")
            await event.context.respond("An error occurred while handling another error!")