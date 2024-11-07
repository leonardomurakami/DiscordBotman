import lightbulb
import hikari

from base.command import BaseCommand


class RemoveCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "remove"
        self.description = "Remove a track from the queue"
        self.help_text = "!remove <position> or /remove <position> - Remove a track from the queue"

    def create_command(self) -> lightbulb.Command:
        @self.plugin.command
        @lightbulb.add_checks(lightbulb.guild_only)
        @lightbulb.option("position", "Queue position to remove", type=int, required=True)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd

    async def execute(self, ctx: lightbulb.Context) -> None:
        player = ctx.bot.d.ongaku.create_player(ctx.guild_id)
        
        if not player.connected or not player.queue:
            await ctx.respond("Queue is empty!")
            return
            
        try:
            position = ctx.options.position - 1
            if 0 <= position < len(player.queue):
                removed_track = player.queue[position]
                player.remove(position)
                await ctx.respond(f"Removed: {removed_track.info.title}")
            else:
                await ctx.respond("Invalid queue position!")
        except Exception as e:
            await ctx.respond(f"Failed to remove track: {str(e)}")