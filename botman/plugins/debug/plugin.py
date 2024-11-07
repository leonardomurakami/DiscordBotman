import lightbulb

from base.plugin import BasePlugin
from .commands.hello import HelloCommand
from .commands.ping import PingCommand
from .commands.sysinfo import SysInfoCommand
from .commands.eval import EvalCommand


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