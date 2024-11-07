import lightbulb
import hikari
import random

from base.command import BaseCommand


class FlipCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "flip"
        self.description = "Flip a coin"
        self.help_text = "!flip or /flip - Flips a coin"

    def create_command(self) -> lightbulb.Command:
        @self.plugin.command
        @lightbulb.set_help(self.help_text)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd

    async def execute(self, ctx: lightbulb.Context) -> None:
        result = random.choice(["Heads", "Tails"])
        embed = hikari.Embed(
            title="Coin Flip",
            description=f"🪙 The coin landed on **{result}**!",
            color=hikari.Color(0xffd700)
        )
        await ctx.respond(embed=embed)