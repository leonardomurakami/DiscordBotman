import os
import lightbulb

from base.plugin import BasePlugin
from .commands.join import JoinCommand
from .commands._play import PlayCommand
from .commands._queue import QueueCommand
from .commands.volume import VolumeCommand
from .commands._skip import SkipCommand
from .commands.seek import SeekCommand
from .commands._clear import ClearCommand
from .commands._shuffle import ShuffleCommand
from .commands._remove import RemoveCommand
from .commands._autoplay import AutoplayCommand
from .commands._stop import StopCommand
from .commands._leave import LeaveCommand


class MusicPlugin(BasePlugin):
    @property
    def plugin_name(self) -> str:
        return "music"
        
    @property
    def plugin_description(self) -> str:
        return "Music commands for playing audio in voice channels"
        
    def _setup_commands(self) -> None:
        self.commands = [
            JoinCommand(self.plugin),
            PlayCommand(self.plugin),
            QueueCommand(self.plugin),
            VolumeCommand(self.plugin),
            SkipCommand(self.plugin),
            SeekCommand(self.plugin),
            ClearCommand(self.plugin),
            ShuffleCommand(self.plugin),
            RemoveCommand(self.plugin),
            AutoplayCommand(self.plugin),
            StopCommand(self.plugin),
            LeaveCommand(self.plugin)
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