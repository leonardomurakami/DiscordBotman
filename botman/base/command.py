from abc import ABC, abstractmethod
import lightbulb

class BaseCommand(ABC):
    """Base class for all bot commands"""
    
    def __init__(self, plugin: lightbulb.Plugin):
        self.plugin = plugin
        self.name: str = ""
        self.description: str = ""
        self.help_text: str = ""
        self._setup_command()
    
    @abstractmethod
    def _setup_command(self) -> None:
        """Configure command properties"""
        pass
        
    @abstractmethod
    async def execute(self, ctx: lightbulb.Context) -> None:
        """Execute command logic"""
        pass
        
    def create_command(self) -> lightbulb.Command:
        """Create and return the lightbulb command"""
        @self.plugin.command
        @lightbulb.set_help(self.help_text)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd