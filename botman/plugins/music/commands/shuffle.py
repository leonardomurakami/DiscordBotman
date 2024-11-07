import lightbulb
import hikari

from base.command import BaseCommand


class ShuffleCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "shuffle"
        self.description = "Shuffle the queue"
        self.help_text = "!shuffle or /shuffle - Shuffle the queue"

    def create_command(self) -> lightbulb.Command:
        @self.bot.command
        @lightbulb.add_checks(lightbulb.guild_only)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd

    async def execute(self, ctx: lightbulb.Context) -> None:
        player = ctx.bot.d.ongaku.create_player(ctx.guild_id)
        
        if not player.connected or len(player.queue) < 2:
            await ctx.respond("Not enough tracks in the queue to shuffle!")
            return
            
        player.shuffle()
        await ctx.respond("Queue shuffled!")