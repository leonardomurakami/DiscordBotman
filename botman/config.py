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

# GLOBALS
SNIPE_TIMEOUT = 10