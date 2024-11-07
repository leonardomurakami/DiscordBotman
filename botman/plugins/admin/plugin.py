import lightbulb

from base.plugin import BasePlugin
from .commands._kick import KickCommand
from .commands._ban import BanCommand
from .commands._purge import PurgeCommand
from .commands._mute import MuteCommand


class AdminPlugin(BasePlugin):
    @property
    def plugin_name(self) -> str:
        return "admin"
        
    @property
    def plugin_description(self) -> str:
        return "Administrative commands for server management"
        
    def _setup_commands(self) -> None:
        self.commands = [
            KickCommand(self.plugin),
            BanCommand(self.plugin),
            PurgeCommand(self.plugin),
            MuteCommand(self.plugin)
        ]

def load(bot: lightbulb.BotApp) -> None:
    plugin = AdminPlugin(bot)
    plugin.load()

def unload(bot: lightbulb.BotApp) -> None:
    plugin = AdminPlugin(bot)
    plugin.unload()