import hikari
import lightbulb

from base.command import BaseCommand


class SlowModeCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "slowmode"
        self.description = "Set channel slowmode"
        self.help_text = "!slowmode <duration> or /slowmode - Set channel slowmode (0 to disable)"

    def create_command(self) -> lightbulb.Command:
        @self.bot.command
        @lightbulb.set_help(self.help_text)
        @lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_CHANNELS))
        @lightbulb.option("duration", "Slowmode duration in seconds (0 to disable)", type=int, required=True)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd

    async def execute(self, ctx: lightbulb.Context) -> None:
        duration = max(0, min(ctx.options.duration, 21600))
        
        try:
            await ctx.get_channel().edit(rate_limit_per_user=duration)
            
            description = "Slowmode has been disabled" if duration == 0 else f"Slowmode set to {duration} seconds"
            embed = hikari.Embed(title="Slowmode Updated", description=description, color=hikari.Color(0x2ecc71))
            await ctx.respond(embed=embed)
        except Exception as e:
            await ctx.respond(f"Failed to set slowmode: {str(e)}")