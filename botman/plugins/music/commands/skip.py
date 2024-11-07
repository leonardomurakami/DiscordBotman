import lightbulb
import hikari

from base.command import BaseCommand


class SkipCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "skip"
        self.description = "Skip the current track"
        self.help_text = "!skip or /skip - Skip the current track"

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
        
        if not player.connected or not player.queue:
            await ctx.respond("Nothing is playing!")
            return
            
        await player.skip()
        await ctx.respond("Skipped the current track!")