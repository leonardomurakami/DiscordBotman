import lightbulb

from base.plugin import BasePlugin
from .commands.kick import KickCommand
from .commands.ban import BanCommand
from .commands.purge import PurgeCommand
from .commands.mute import MuteCommand


class AdminPlugin(BasePlugin):
    @property
    def plugin_name(self) -> str:
        return "admin"
        
    @property
    def plugin_description(self) -> str:
        return "Administrative commands for server management"
        
    def _setup_commands(self) -> None:
        self.commands = [
            KickCommand(self),
            BanCommand(self),
            PurgeCommand(self),
            MuteCommand(self)
        ]

def load(bot: lightbulb.BotApp) -> None:
    plugin = AdminPlugin(bot)
    plugin.load()

def unload(bot: lightbulb.BotApp) -> None:
    plugin = AdminPlugin(bot)
    plugin.unload()