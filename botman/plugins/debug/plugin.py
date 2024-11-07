import lightbulb

from base.plugin import BasePlugin
from .commands._hello import HelloCommand
from .commands._ping import PingCommand
from .commands._sysinfo import SysInfoCommand
from .commands._eval import EvalCommand


class DebugPlugin(BasePlugin):
    @property
    def plugin_name(self) -> str:
        return "debug"
        
    @property
    def plugin_description(self) -> str:
        return "Debug and system information commands"
        
    def _setup_commands(self) -> None:
        self.commands = [
            HelloCommand(self.plugin),
            PingCommand(self.plugin),
            SysInfoCommand(self.plugin),
            EvalCommand(self.plugin)
        ]


def load(bot: lightbulb.BotApp) -> None:
    plugin = DebugPlugin(bot)
    plugin.load()


def unload(bot: lightbulb.BotApp) -> None:
    plugin = DebugPlugin(bot)
    plugin.unload()