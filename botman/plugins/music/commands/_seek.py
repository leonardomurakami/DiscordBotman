import lightbulb
import hikari

from base.command import BaseCommand


class SeekCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "seek"
        self.description = "Seek to a position in the current track"
        self.help_text = "!seek <seconds> or /seek <seconds> - Seek to a position in the current track"

    def create_command(self) -> lightbulb.Command:
        @self.plugin.command
        @lightbulb.add_checks(lightbulb.guild_only)
        @lightbulb.option("seconds", "Number of seconds to seek", type=int, required=True)
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
        
        try:
            position = ctx.options.seconds * 1000
            current_track = player.queue[0]
            
            if position < 0 or position > current_track.info.length:
                await ctx.respond("Invalid position! Must be within track duration.")
                return
                
            await player.set_position(position)
            minutes, seconds = divmod(position // 1000, 60)
            await ctx.respond(f"Seeked to position: {minutes:02d}:{seconds:02d}")
        except Exception as e:
            await ctx.respond(f"Failed to seek: {str(e)}")