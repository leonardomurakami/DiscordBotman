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
            FlipCommand(self),
            RollCommand(self),
            Magic8BallCommand(self),
            RPSCommand(self),
            WakeCommand(self)
        ]

def load(bot: lightbulb.BotApp) -> None:
    plugin = FunPlugin(bot)
    plugin.load()

def unload(bot: lightbulb.BotApp) -> None:
    plugin = FunPlugin(bot)
    plugin.unload()