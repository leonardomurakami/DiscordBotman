import os
from dataclasses import dataclass

# DATACLASSES
@dataclass
class LavalinkConfig:
    host: str = os.getenv("LAVALINK_SERVER_HOST", "lavalink")
    port: int = int(os.getenv("LAVALINK_SERVER_PORT", 2333))
    password: str = os.getenv("LAVALINK_SERVER_PASSWORD", "youshallnotpass")

@dataclass
class BotConfig:
    token: str = os.getenv("DISCORD_BOT_TOKEN", "")
    prefix: str = "!"
    owner_ids: list[int] = None
    
    def __post_init__(self):
        if self.owner_ids is None:
            self.owner_ids = [int(os.getenv("DISCORD_BOT_OWNER_ID", "0"))]

@dataclass
class LogConfig:
    """Configuration class for logging settings."""
    
    def __init__(
        self,
        level: str = "INFO",
        format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        file_path: str = "logs/bot.log",
        max_bytes: int = 10_485_760,  # 10MB
        backup_count: int = 5
    ):
        """
        Initialize logging configuration.

        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            format: Log message format string
            file_path: Path to log file
            max_bytes: Maximum size of log file before rotation
            backup_count: Number of backup files to keep
        """
        self.level: str = level.upper()
        self.format: str = format
        self.file_path: str = file_path
        self.max_bytes: int = max_bytes
        self.backup_count: int = backup_count
        
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
    
    @property
    def formatted_level(self) -> str:
        """Return the logging level in the correct format."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        return self.level if self.level in valid_levels else "INFO"
    
    def update_level(self, new_level: str) -> None:
        """
        Update the logging level.
        
        Args:
            new_level: New logging level to set
        """
        self.level = new_level.upper()
    
    def update_format(self, new_format: str) -> None:
        """
        Update the log format string.
        
        Args:
            new_format: New format string to use
        """
        self.format = new_format
    
    def update_file_path(self, new_path: str) -> None:
        """
        Update the log file path and create directories if needed.
        
        Args:
            new_path: New file path for logs
        """
        self.file_path = new_path
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

# GLOBALS
SNIPE_TIMEOUT = 10