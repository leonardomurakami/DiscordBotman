import lightbulb
import hikari

from base.command import BaseCommand


class BanCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "ban"
        self.description = "Ban a user from the server"
        self.help_text = "!ban <user> <reason> or /ban <user> <reason> - Bans a user from the server"

    def create_command(self) -> lightbulb.Command:
        @self.plugin.command
        @lightbulb.set_help(self.help_text)
        @lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.BAN_MEMBERS))
        @lightbulb.option("reason", "Reason for the ban", type=str, required=False, default="No reason provided")
        @lightbulb.option("user", "The user to ban", type=hikari.User, required=True)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd

    async def execute(self, ctx: lightbulb.Context) -> None:
        target = ctx.options.user
        reason = ctx.options.reason
        
        try:
            await ctx.get_guild().ban(target, reason=f"Banned by {ctx.author}: {reason}")
            embed = hikari.Embed(
                title="User Banned",
                description=f"Successfully banned {target.mention}",
                color=hikari.Color(0xff0000)
            )
            embed.add_field("Reason", reason)
            await ctx.respond(embed=embed)
        except Exception as e:
            await ctx.respond(f"Failed to ban user: {str(e)}")