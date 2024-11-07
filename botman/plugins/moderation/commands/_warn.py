import datetime
import hikari
import lightbulb

from base.command import BaseCommand


class WarnCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "warn"
        self.description = "Warn a user"
        self.help_text = "!warn <user> <reason> or /warn - Warn a user"

    def create_command(self) -> lightbulb.Command:
        @self.plugin.command
        @lightbulb.set_help(self.help_text)
        @lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MODERATE_MEMBERS))
        @lightbulb.option("reason", "Reason for the warning", type=str, required=True)
        @lightbulb.option("user", "The user to warn", type=hikari.User, required=True)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd

    async def execute(self, ctx: lightbulb.Context) -> None:
        target = ctx.options.user
        reason = ctx.options.reason

        if not hasattr(ctx.bot, 'warnings'):
            ctx.bot.warnings = {}
        
        if ctx.guild_id not in ctx.bot.warnings:
            ctx.bot.warnings[ctx.guild_id] = {}
        
        if target.id not in ctx.bot.warnings[ctx.guild_id]:
            ctx.bot.warnings[ctx.guild_id][target.id] = []
        
        ctx.bot.warnings[ctx.guild_id][target.id].append({
            'reason': reason,
            'mod': ctx.author.id,
            'time': datetime.datetime.now()
        })

        embed = hikari.Embed(
            title="User Warned",
            description=f"{target.mention} has been warned",
            color=hikari.Color(0xff9900)
        )
        embed.add_field("Reason", reason)
        embed.add_field("Total Warnings", str(len(ctx.bot.warnings[ctx.guild_id][target.id])))
        
        await ctx.respond(embed=embed)
        
        try:
            user_embed = hikari.Embed(
                title="Warning Received",
                description=f"You have been warned in {ctx.get_guild().name}",
                color=hikari.Color(0xff9900)
            )
            user_embed.add_field("Reason", reason)
            await target.send(embed=user_embed)
        except:
            await ctx.respond("Note: Could not DM user about the warning.")