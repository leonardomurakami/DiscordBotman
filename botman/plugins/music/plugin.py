import os
import lightbulb

from base.plugin import BasePlugin
from .commands.join import JoinCommand
from .commands.play import PlayCommand
from .commands.queue import QueueCommand
from .commands.volume import VolumeCommand
from .commands.skip import SkipCommand
from .commands.seek import SeekCommand
from .commands.clear import ClearCommand
from .commands.shuffle import ShuffleCommand
from .commands.remove import RemoveCommand
from .commands.autoplay import AutoplayCommand
from .commands.stop import StopCommand
from .commands.leave import LeaveCommand


class MusicPlugin(BasePlugin):
    @property
    def plugin_name(self) -> str:
        return "music"
        
    @property
    def plugin_description(self) -> str:
        return "Music commands for playing audio in voice channels"
        
    def _setup_commands(self) -> None:
        self.commands = [
            JoinCommand(self.bot),
            PlayCommand(self.bot),
            QueueCommand(self.bot),
            VolumeCommand(self.bot),
            SkipCommand(self.bot),
            SeekCommand(self.bot),
            ClearCommand(self.bot),
            ShuffleCommand(self.bot),
            RemoveCommand(self.bot),
            AutoplayCommand(self.bot),
            StopCommand(self.bot),
            LeaveCommand(self.bot)
        ]


def load(bot: lightbulb.BotApp) -> None:
    enable_lavalink = os.getenv("ENABLE_LAVALINK", False)
    
    if enable_lavalink:
        plugin = MusicPlugin(bot)
        plugin.load()


def unload(bot: lightbulb.BotApp) -> None:
    enable_lavalink = os.getenv("ENABLE_LAVALINK", False)

    if enable_lavalink:
        plugin = MusicPlugin(bot)
        plugin.unload()