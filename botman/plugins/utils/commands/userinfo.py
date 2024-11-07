import lightbulb
import hikari

from base.command import BaseCommand


class UserInfoCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "userinfo"
        self.description = "Get detailed information about a user"
        self.help_text = "!userinfo <user> or /userinfo <user> - Shows detailed information about a user"

    def create_command(self) -> lightbulb.Command:
        @self.bot.command
        @lightbulb.set_help(self.help_text)
        @lightbulb.option("user", "The user to get information about", type=hikari.User, required=False)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd

    async def execute(self, ctx: lightbulb.Context) -> None:
        target = ctx.options.user or ctx.author
        member = ctx.get_guild().get_member(target.id)
        
        roles = [role.mention for role in member.get_roles()] if member else []
        roles_str = ", ".join(roles) if roles else "No roles"
        
        embed = hikari.Embed(
            title="User Information",
            color=hikari.Color(0x3498db)
        )
        
        embed.set_thumbnail(target.avatar_url)
        embed.add_field("Username", str(target), inline=True)
        embed.add_field("ID", str(target.id), inline=True)
        embed.add_field("Bot", "Yes" if target.is_bot else "No", inline=True)
        embed.add_field("Account Created", f"<t:{int(target.created_at.timestamp())}:R>", inline=True)
        
        if member:
            embed.add_field("Joined Server", f"<t:{int(member.joined_at.timestamp())}:R>", inline=True)
            embed.add_field("Roles", roles_str, inline=False)
        
        await ctx.respond(embed=embed)