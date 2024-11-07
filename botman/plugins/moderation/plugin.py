import lightbulb

from base.plugin import BasePlugin
from .commands.slowmode import SlowModeCommand
from .commands.warn import WarnCommand
from .commands.warnings import WarningsCommand
from .commands.clearwarnings import ClearWarningsCommand


class ModerationPlugin(BasePlugin):
    @property
    def plugin_name(self) -> str:
        return "moderation"
        
    @property
    def plugin_description(self) -> str:
        return "Advanced moderation commands for server management"
        
    def _setup_commands(self) -> None:
        self.commands = [
            SlowModeCommand(self.plugin),
            WarnCommand(self.plugin),
            WarningsCommand(self.plugin),
            ClearWarningsCommand(self.plugin)
        ]


def load(bot: lightbulb.BotApp) -> None:
    plugin = ModerationPlugin(bot)
    plugin.load()


def unload(bot: lightbulb.BotApp) -> None:
    plugin = ModerationPlugin(bot)
    plugin.unload()