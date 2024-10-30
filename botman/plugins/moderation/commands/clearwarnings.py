import hikari
import lightbulb

from base.command import BaseCommand


class ClearWarningsCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "clearwarnings"
        self.description = "Clear all warnings for a user"
        self.help_text = "!clearwarnings <user> or /clearwarnings - Clear all warnings for a user"

    def create_command(self) -> lightbulb.Command:
        @self.bot.command
        @lightbulb.set_help(self.help_text)
        @lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MODERATE_MEMBERS))
        @lightbulb.option("user", "The user to clear warnings for", type=hikari.User, required=True)
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
            await ctx.respond(f"{target.mention} has no warnings to clear.")
            return
        
        warning_count = len(ctx.bot.warnings[ctx.guild_id][target.id])
        del ctx.bot.warnings[ctx.guild_id][target.id]
        
        embed = hikari.Embed(
            title="Warnings Cleared",
            description=f"Cleared {warning_count} warning(s) for {target.mention}",
            color=hikari.Color(0x2ecc71)
        )
        await ctx.respond(embed=embed)