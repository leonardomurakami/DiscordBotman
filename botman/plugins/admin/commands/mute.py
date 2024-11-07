import lightbulb
import hikari
import datetime

from base.command import BaseCommand


class MuteCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "mute"
        self.description = "Timeout a user"
        self.help_text = "!mute <user> <duration> <reason> or /mute <user> <duration> <reason> - Timeout a user"

    def create_command(self) -> lightbulb.Command:
        @self.bot.command
        @lightbulb.set_help(self.help_text)
        @lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MODERATE_MEMBERS))
        @lightbulb.option("reason", "Reason for the mute", type=str, required=False, default="No reason provided")
        @lightbulb.option("duration", "Duration in minutes", type=int, required=True)
        @lightbulb.option("user", "The user to mute", type=hikari.User, required=True)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd

    async def execute(self, ctx: lightbulb.Context) -> None:
        target = ctx.options.user
        duration = ctx.options.duration
        reason = ctx.options.reason
        
        try:
            until = datetime.datetime.now() + datetime.timedelta(minutes=duration)
            await ctx.get_guild().edit_member(target, communication_disabled_until=until)
            
            embed = hikari.Embed(
                title="User Muted",
                description=f"Successfully muted {target.mention}",
                color=hikari.Color(0xff6600)
            )
            embed.add_field("Duration", f"{duration} minutes")
            embed.add_field("Reason", reason)
            await ctx.respond(embed=embed)
        except Exception as e:
            await ctx.respond(f"Failed to mute user: {str(e)}")