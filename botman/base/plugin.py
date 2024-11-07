from abc import ABC, abstractmethod
import typing
import lightbulb
from base.command import BaseCommand

class BasePlugin(ABC):
    """Base class for all plugins"""
    
    def __init__(self, bot: lightbulb.BotApp):
        self.bot = bot
        self.plugin = lightbulb.Plugin(self.plugin_name)
        self.plugin.description = self.plugin_description
        self.commands: typing.List[BaseCommand] = []
        self._setup_commands()
        self._register_commands()
        
    @property
    @abstractmethod
    def plugin_name(self) -> str:
        """Name of the plugin"""
        pass
        
    @property
    @abstractmethod
    def plugin_description(self) -> str:
        """Description of the plugin"""
        pass
        
    @abstractmethod
    def _setup_commands(self) -> None:
        """Initialize plugin commands"""
        pass
        
    def _register_commands(self) -> None:
        """Register all commands with the plugin"""
        for command in self.commands:
            self.plugin.command(command.create_command())
            
    def load(self) -> None:
        """Load plugin into bot"""
        self.add_plugin(self.plugin)
        
    def unload(self) -> None:
        """Unload plugin from bot"""
        self.remove_plugin(self.plugin)
