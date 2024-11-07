import lightbulb
import hikari
import datetime
import config

from base.command import BaseCommand


class SnipeCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "snipe"
        self.description = "Show the last deleted message"
        self.help_text = "!snipe or /snipe - Shows the last deleted message in the channel"

    def create_command(self) -> lightbulb.Command:
        @self.plugin.command
        @lightbulb.set_help(self.help_text)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd

    async def execute(self, ctx: lightbulb.Context) -> None:
        channel_id = ctx.channel_id
        
        if channel_id not in ctx.bot.d.deleted_messages:
            await ctx.respond("There are no recently deleted messages to snipe! 🎯❌")
            return
        
        deleted = ctx.bot.d.deleted_messages[channel_id]
        
        if datetime.datetime.now() - deleted['time'] > datetime.timedelta(minutes=config.SNIPE_TIMEOUT):
            del ctx.bot.d.deleted_messages[channel_id]
            await ctx.respond("The last deleted message is too old to snipe! 🎯⏰")
            return
        
        embed = hikari.Embed(
            title="🎯 Sniped Message",
            description=deleted['content'] if deleted['content'] else "[No text content]",
            color=hikari.Color(0xff6b6b),
            timestamp=deleted['time']
        )
        
        embed.set_author(
            name=f"{deleted['author'].username}#{deleted['author'].discriminator}",
            icon=deleted['author'].avatar_url
        )
        
        if deleted['attachments']:
            attachment_names = [a.filename for a in deleted['attachments']]
            embed.add_field(
                name="📎 Attachments",
                value="\n".join(attachment_names),
                inline=False
            )
        
        embed.set_footer(text="Message deleted at")
        
        await ctx.respond(embed=embed)