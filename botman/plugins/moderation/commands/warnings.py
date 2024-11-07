import hikari
import lightbulb

from base.command import BaseCommand


class WarningsCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "warnings"
        self.description = "Check a user's warnings"
        self.help_text = "!warnings <user> or /warnings - Check a user's warnings"

    def create_command(self) -> lightbulb.Command:
        @self.bot.command
        @lightbulb.set_help(self.help_text)
        @lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MODERATE_MEMBERS))
        @lightbulb.option("user", "The user to check", type=hikari.User, required=True)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd

    async def execute(self, ctx: lightbulb.Context) -> None:
        target = ctx.options.user
        
        if not hasattr(ctx.bot, 'warnings') or \
           ctx.guild_id not in ctx.bot.warnings or \
           target.id not in ctx.bot.warnings[ctx.guild_id]:
            embed = hikari.Embed(
                title="User Warnings",
                description=f"{target.mention} has no warnings",
                color=hikari.Color(0x2ecc71)
            )
            await ctx.respond(embed=embed)
            return
        
        warnings = ctx.bot.warnings[ctx.guild_id][target.id]
        embed = hikari.Embed(
            title="User Warnings",
            description=f"{target.mention} has {len(warnings)} warning(s)",
            color=hikari.Color(0xff9900)
        )
        
        for idx, warning in enumerate(warnings, 1):
            mod = ctx.bot.cache.get_user(warning['mod'])
            mod_name = mod.username if mod else "Unknown Moderator"
            time_str = warning['time'].strftime("%Y-%m-%d %H:%M:%S")
            
            embed.add_field(
                name=f"Warning {idx}",
                value=f"**Reason:** {warning['reason']}\n"
                      f"**Moderator:** {mod_name}\n"
                      f"**Time:** {time_str}",
                inline=False
            )
        
        await ctx.respond(embed=embed)