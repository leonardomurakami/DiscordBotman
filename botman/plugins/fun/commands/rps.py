import lightbulb
import hikari

from base.command import BaseCommand
from views.rps_view import RPSView


class RPSCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "rps"
        self.description = "Play Rock, Paper, Scissors"
        self.help_text = "!rps or /rps - Play Rock, Paper, Scissors using buttons"

    def create_command(self) -> lightbulb.Command:
        @self.bot.command
        @lightbulb.set_help(self.help_text)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd

    async def execute(self, ctx: lightbulb.Context) -> None:
        embed = hikari.Embed(
            title="Rock, Paper, Scissors",
            description="Choose your move!",
            color=hikari.Color(0x3498db)
        )
        embed.add_field(
            name="How to Play",
            value="• Click a button to make your move\n"
                  "• Rock beats Scissors\n"
                  "• Paper beats Rock\n"
                  "• Scissors beats Paper",
            inline=False
        )
        
        view = RPSView(ctx.author)
        message = await ctx.respond(embed=embed, components=view.build())
        
        ctx.app.d.miru.start_view(view)
        await view.wait()
        
        if view.user_choice is None:
            embed.description = "Game timed out! Please try again."
            await message.edit(embed=embed, components=[])