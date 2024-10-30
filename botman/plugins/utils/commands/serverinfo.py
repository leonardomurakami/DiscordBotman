import lightbulb
import hikari

from base.command import BaseCommand


class ServerInfoCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "serverinfo"
        self.description = "Get detailed information about the server"
        self.help_text = "!serverinfo or /serverinfo - Shows detailed information about the server"

    def create_command(self) -> lightbulb.Command:
        @self.bot.command
        @lightbulb.set_help(self.help_text)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd

    async def execute(self, ctx: lightbulb.Context) -> None:
        guild = ctx.get_guild()
        
        embed = hikari.Embed(
            title=f"{guild.name} - Server Information",
            color=hikari.Color(0x2ecc71)
        )
        
        if guild.icon_url:
            embed.set_thumbnail(guild.icon_url)
        
        embed.add_field("Owner", f"<@{guild.owner_id}>", inline=True)
        embed.add_field("Created", f"<t:{int(guild.created_at.timestamp())}:R>", inline=True)
        embed.add_field("Members", str(guild.member_count), inline=True)
        embed.add_field("Channels", str(len(guild.get_channels())), inline=True)
        embed.add_field("Roles", str(len(guild.get_roles())), inline=True)
        embed.add_field("Boost Level", str(guild.premium_tier), inline=True)
        
        await ctx.respond(embed=embed)