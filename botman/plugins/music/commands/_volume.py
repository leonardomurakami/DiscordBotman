import lightbulb

from base.command import BaseCommand


class VolumeCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "volume"
        self.description = "Set the playback volume"
        self.help_text = "!volume <volume> or /volume <volume> - Set the playback volume"

    def create_command(self) -> lightbulb.Command:
        @self.plugin.command
        @lightbulb.add_checks(lightbulb.guild_only)
        @lightbulb.option("volume", "Volume level (0-150)", type=int, min_value=0, max_value=150, required=True)
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
            
        await player.set_volume(ctx.options.volume)
        await ctx.respond(f"Volume set to {ctx.options.volume}%")