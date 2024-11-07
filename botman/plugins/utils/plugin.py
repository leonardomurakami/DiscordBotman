import lightbulb

from base.plugin import BasePlugin
from .commands.userinfo import UserInfoCommand
from .commands.serverinfo import ServerInfoCommand
from .commands.poll import PollCommand
from .commands.remind import RemindCommand
from .commands.password import PasswordCommand
from .commands.snipe import SnipeCommand
from .commands.editsnipe import EditSnipeCommand


class UtilsPlugin(BasePlugin):
    @property
    def plugin_name(self) -> str:
        return "utility"
        
    @property
    def plugin_description(self) -> str:
        return "Utility commands for server management and information"
        
    def _setup_commands(self) -> None:
        self.commands = [
            UserInfoCommand(self.bot),
            ServerInfoCommand(self.bot),
            PollCommand(self.bot),
            RemindCommand(self.bot),
            PasswordCommand(self.bot),
            SnipeCommand(self.bot),
            EditSnipeCommand(self.bot)
        ]

def load(bot: lightbulb.BotApp) -> None:
    plugin = UtilsPlugin(bot)
    plugin.load()

def unload(bot: lightbulb.BotApp) -> None:
    plugin = UtilsPlugin(bot)
    plugin.unload()