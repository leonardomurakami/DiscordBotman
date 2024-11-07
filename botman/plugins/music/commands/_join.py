import lightbulb
import hikari
import logging

from base.command import BaseCommand


class JoinCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "join"
        self.description = "Join your voice channel"
        self.help_text = "!join or /join - Join your voice channel"

    def create_command(self) -> lightbulb.Command:
        @self.plugin.command
        @lightbulb.add_checks(lightbulb.guild_only)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd

    async def execute(self, ctx: lightbulb.Context) -> None:
        states = ctx.bot.cache.get_voice_states_view_for_guild(ctx.guild_id)
        voice_state = [state for state in states.values() if state.user_id == ctx.author.id]
        
        if not voice_state:
            await ctx.respond("You're not in a voice channel!")
            return
            
        channel_id = voice_state[0].channel_id
        try:
            player = ctx.bot.d.ongaku.create_player(ctx.guild_id)
            await player.connect(channel_id, deaf=True)
            await ctx.respond(f"Joined <#{channel_id}>!")
        except Exception as e:
            logging.error(f"Failed to join voice channel: {e}")
            await ctx.respond(f"Failed to join voice channel: {str(e)}")