import lightbulb
import hikari

from base.command import BaseCommand


class KickCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "kick"
        self.description = "Kick a user from the server"
        self.help_text = "!kick <user> <reason> or /kick <user> <reason> - Kicks a user from the server"

    def create_command(self) -> lightbulb.Command:
        @self.bot.command
        @lightbulb.set_help(self.help_text)
        @lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.KICK_MEMBERS))
        @lightbulb.option("reason", "Reason for the kick", type=str, required=False, default="No reason provided")
        @lightbulb.option("user", "The user to kick", type=hikari.User, required=True)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd

    async def execute(self, ctx: lightbulb.Context) -> None:
        target = ctx.options.user
        reason = ctx.options.reason
        
        try:
            await ctx.get_guild().kick(target, reason=f"Kicked by {ctx.author}: {reason}")
            embed = hikari.Embed(
                title="User Kicked",
                description=f"Successfully kicked {target.mention}",
                color=hikari.Color(0xff9900)
            )
            embed.add_field("Reason", reason)
            await ctx.respond(embed=embed)
        except Exception as e:
            await ctx.respond(f"Failed to kick user: {str(e)}")