import lightbulb
import hikari
from datetime import datetime

from base.command import BaseCommand

class EditSnipeCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "editsnipe"
        self.description = "Show recently edited messages"
        self.help_text = "!editsnipe or /editsnipe - Show the most recently edited message"

    def create_command(self) -> lightbulb.Command:
        @self.plugin.command
        @lightbulb.set_help(self.help_text)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd

    async def execute(self, ctx: lightbulb.Context) -> None:
        messages = await ctx.bot.d.api_client.get_recent_edited_messages(str(ctx.guild_id))
        
        if not messages:
            embed = hikari.Embed(
                title="No Messages Found",
                description="There are no recently edited messages to show.",
                color=hikari.Color(0xff0000)
            )
            await ctx.respond(embed=embed)
            return

        message = messages[0]  # Get most recent
        embed = hikari.Embed(
            title="Edited Message",
            color=hikari.Color(0x00ff00)
        )
        embed.add_field("Before", message["old_content"] or "*No content*")
        embed.add_field("After", message["new_content"] or "*No content*")
        embed.add_field("Author", f"<@{message['author_id']}>")
        embed.add_field("Channel", f"<#{message['channel_id']}>")
        embed.set_footer(text=f"Message ID: {message['message_id']}")
        
        await ctx.respond(embed=embed)