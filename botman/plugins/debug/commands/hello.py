import lightbulb
import hikari

from base.command import BaseCommand


class HelloCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "hello"
        self.description = "Says hello to the user"
        self.help_text = "!hello or /hello - Simple greeting command to test if the bot is responsive"

    def create_command(self) -> lightbulb.Command:
        @self.plugin.command
        @lightbulb.set_help(self.help_text)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd

    async def execute(self, ctx: lightbulb.Context) -> None:
        await ctx.respond(f"Hello, {ctx.author.mention}!")