import lightbulb
import hikari
import datetime

from base.command import BaseCommand


class PurgeCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "purge"
        self.description = "Delete multiple messages"
        self.help_text = "!purge <amount> or /purge <amount> - Deletes specified number of messages"

    def create_command(self) -> lightbulb.Command:
        @self.bot.command
        @lightbulb.set_help(self.help_text)
        @lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_MESSAGES))
        @lightbulb.option("amount", "Number of messages to delete", type=int, required=True)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd

    async def execute(self, ctx: lightbulb.Context) -> None:
        amount = min(max(1, ctx.options.amount), 100)
        
        try:
            messages = (
                await ctx.bot.rest.fetch_messages(ctx.channel_id)
                .take_until(lambda m: datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=14) > m.created_at)
                .limit(amount)
            )
            await ctx.get_channel().delete_messages(messages)
            
            embed = hikari.Embed(
                title="Messages Purged",
                description=f"Successfully deleted {len(messages)} messages",
                color=hikari.Color(0x00ff00)
            )
            await ctx.respond(embed=embed, delete_after=5)
        except Exception as e:
            await ctx.respond(f"Failed to purge messages: {str(e)}")