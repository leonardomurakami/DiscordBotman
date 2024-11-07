import lightbulb
import hikari
import datetime
import config

from base.command import BaseCommand


class EditSnipeCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "editsnipe"
        self.description = "Show the last edited message"
        self.help_text = "!editsnipe or /editsnipe - Shows the last edited message in the channel"

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
        
        if channel_id not in ctx.bot.d.edited_messages:
            await ctx.respond("There are no recently edited messages to snipe! ✏️❌")
            return
        
        edited = ctx.bot.d.edited_messages[channel_id]
        
        if datetime.datetime.now() - edited['time'] > datetime.timedelta(minutes=config.SNIPE_TIMEOUT):
            del ctx.bot.d.edited_messages[channel_id]
            await ctx.respond("The last edited message is too old to snipe! ✏️⏰")
            return
        
        embed = hikari.Embed(
                title="✏️ Sniped Edit",
                color=hikari.Color(0xffd93d),
                timestamp=edited['time']
            )
            
        embed.set_author(
            name=f"{edited['author'].username}#{edited['author'].discriminator}",
            icon=edited['author'].avatar_url
        )
        
        embed.add_field(
            name="Before",
            value=edited['old_content'] if edited['old_content'] else "[No text content]",
            inline=False
        )
        
        embed.add_field(
            name="After",
            value=edited['new_content'] if edited['new_content'] else "[No text content]",
            inline=False
        )
        
        embed.set_footer(text="Message edited at")
        
        await ctx.respond(embed=embed)