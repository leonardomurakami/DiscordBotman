import lightbulb

from base.plugin import BasePlugin
from .commands.flip import FlipCommand
from .commands.roll import RollCommand
from .commands.eightball import Magic8BallCommand
from .commands.rps import RPSCommand
from .commands.wake import WakeCommand

class FunPlugin(BasePlugin):
    @property
    def plugin_name(self) -> str:
        return "fun"
        
    @property
    def plugin_description(self) -> str:
        return "Fun and entertainment commands"
        
    def _setup_commands(self) -> None:
        self.commands = [
            FlipCommand(self.plugin),
            RollCommand(self.plugin),
            Magic8BallCommand(self.plugin),
            RPSCommand(self.plugin),
            WakeCommand(self.plugin)
        ]

def load(bot: lightbulb.BotApp) -> None:
    plugin = FunPlugin(bot)
    plugin.load()

def unload(bot: lightbulb.BotApp) -> None:
    plugin = FunPlugin(bot)
    plugin.unload()