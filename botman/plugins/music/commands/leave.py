import logging
import lightbulb

from base.command import BaseCommand

logger = logging.getLogger(__name__)

class LeaveCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "leave"
        self.description = "Leave the voice channel"
        self.help_text = "!leave or /leave - Leave the voice channel"

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
        
        await self.cleanup_player(ctx.guild_id, ctx.bot)
        await ctx.respond("Left the voice channel!")

    async def cleanup_player(self, guild_id: int, bot: lightbulb.BotApp) -> None:
        try:
            if guild_id in bot.d.active_views:
                view = bot.d.active_views[guild_id]
                try:
                    await view.message.delete()
                except Exception as e:
                    logging.error(f"Failed to delete music player message during cleanup: {e}")
                del bot.d.active_views[guild_id]

            if guild_id in bot.d.voice_timeouts:
                bot.d.voice_timeouts[guild_id].cancel()
                del bot.d.voice_timeouts[guild_id]

            player = bot.d.ongaku.create_player(guild_id)
            if player:
                await player.stop()
                await player.disconnect()
                bot.d.ongaku.delete_player(guild_id)

        except Exception as e:
            logging.error(f"Error during player cleanup: {e}")