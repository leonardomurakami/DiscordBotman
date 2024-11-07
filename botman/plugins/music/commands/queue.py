import lightbulb
import hikari

from base.command import BaseCommand


class QueueCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "queue"
        self.description = "Show the current queue"
        self.help_text = "!queue or /queue - Show the current queue"

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
            
        if not player.queue:
            await ctx.respond("The queue is empty!")
            return
            
        embed = hikari.Embed(
            title="Music Queue",
            color=hikari.Color(0x3498db)
        )
        
        current_track = player.queue[0]
        duration = current_track.info.length // 1000
        minutes, seconds = divmod(duration, 60)
        
        embed.add_field(
            name="Now Playing",
            value=f"🎵 {current_track.info.title}\n`{minutes:02d}:{seconds:02d}` - {current_track.info.author}",
            inline=False
        )
        
        if len(player.queue) > 1:
            upcoming = []
            total_duration = 0
            
            for idx, track in enumerate(player.queue[1:], 1):
                if idx <= 10:
                    duration = track.info.length // 1000
                    minutes, seconds = divmod(duration, 60)
                    upcoming.append(f"`{idx}.` {track.info.title} `({minutes:02d}:{seconds:02d})`")
                total_duration += track.info.length // 1000
            
            queue_text = "\n".join(upcoming)
            
            if len(player.queue) > 11:
                queue_text += f"\n\n*...and {len(player.queue) - 11} more tracks*"
            
            hours, remainder = divmod(total_duration, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            duration_text = f"{hours}h {minutes}m {seconds}s" if hours > 0 else f"{minutes}m {seconds}s"
                
            embed.add_field(
                name=f"Up Next ({len(player.queue) - 1} tracks)",
                value=queue_text,
                inline=False
            )
            
            embed.add_field(
                name="Queue Duration",
                value=duration_text,
                inline=True
            )
        
        status_text = []
        if player.loop:
            status_text.append("🔁 Loop enabled")
        if player.autoplay:
            status_text.append("♾️ Autoplay enabled")
        if player.is_paused:
            status_text.append("⏸️ Paused")
        
        if status_text:
            embed.add_field(
                name="Status",
                value=" | ".join(status_text),
                inline=True
            )
        
        await ctx.respond(embed=embed)