import lightbulb
import hikari

from base.command import BaseCommand


class ClearCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "clear"
        self.description = "Clear the queue"
        self.help_text = "!clear or /clear - Clear the queue"

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
        
        if not player.connected:
            await ctx.respond("Not connected to a voice channel!")
            return
            
        await player.clear()
        await ctx.respond("Queue cleared!")