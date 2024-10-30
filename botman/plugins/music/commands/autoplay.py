import lightbulb
import hikari

from base.command import BaseCommand


class AutoplayCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "autoplay"
        self.description = "Toggle autoplay"
        self.help_text = "!autoplay or /autoplay - Toggle autoplay"

    def create_command(self) -> lightbulb.Command:
        @self.bot.command
        @lightbulb.add_checks(lightbulb.guild_only)
        @lightbulb.option("state", "Enable or disable autoplay", type=bool, required=False)
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
            
        state = ctx.options.state if ctx.options.state is not None else None
        new_state = player.set_autoplay(state)
        status = "enabled" if new_state else "disabled"
        await ctx.respond(f"Autoplay {status}!")