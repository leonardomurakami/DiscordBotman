import lightbulb
import hikari
from datetime import datetime

from base.command import BaseCommand

class SnipeCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "snipe"
        self.description = "Show recently deleted messages"
        self.help_text = "!snipe or /snipe - Show the most recently deleted message"

    def create_command(self) -> lightbulb.Command:
        @self.plugin.command
        @lightbulb.set_help(self.help_text)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd

    async def execute(self, ctx: lightbulb.Context) -> None:
        messages = await ctx.bot.d.api_client.get_recent_deleted_messages(str(ctx.guild_id))
        
        if not messages:
            embed = hikari.Embed(
                title="No Messages Found",
                description="There are no recently deleted messages to show.",
                color=hikari.Color(0xff0000)
            )
            await ctx.respond(embed=embed)
            return

        message = messages[0]  # Get most recent
        embed = hikari.Embed(
            title="Deleted Message",
            color=hikari.Color(0x00ff00)
        )
        embed.add_field("Content", message["content"] or "*No content*")
        embed.add_field("Author", f"<@{message['author_id']}>")
        embed.add_field("Channel", f"<#{message['channel_id']}>")
        embed.set_footer(text=f"Message ID: {message['message_id']}")
        
        await ctx.respond(embed=embed)