import lightbulb
import hikari
import random

from base.command import BaseCommand


class RollCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "roll"
        self.description = "Roll a dice"
        self.help_text = "!roll <sides> or /roll <sides> - Rolls a dice with specified number of sides"

    def create_command(self) -> lightbulb.Command:
        @self.plugin.command
        @lightbulb.set_help(self.help_text)
        @lightbulb.option("sides", "Number of sides on the dice", type=int, default=6)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd

    async def execute(self, ctx: lightbulb.Context) -> None:
        sides = max(2, ctx.options.sides)
        result = random.randint(1, sides)
        embed = hikari.Embed(
            title="Dice Roll",
            description=f"🎲 You rolled a **{result}** (d{sides})!",
            color=hikari.Color(0xff4500)
        )
        await ctx.respond(embed=embed)