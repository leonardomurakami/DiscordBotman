import lightbulb
import hikari
import asyncio

from base.command import BaseCommand


class RemindCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "remind"
        self.description = "Set a reminder"
        self.help_text = "!remind <time> <reminder> or /remind - Set a reminder (time in minutes)"

    def create_command(self) -> lightbulb.Command:
        @self.bot.command
        @lightbulb.set_help(self.help_text)
        @lightbulb.option("reminder", "What to remind you about", type=str, required=True)
        @lightbulb.option("time", "Time in minutes", type=int, required=True)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd

    async def execute(self, ctx: lightbulb.Context) -> None:
        time_minutes = max(1, min(ctx.options.time, 1440))  # Limit to 24 hours
        reminder_text = ctx.options.reminder
        
        embed = hikari.Embed(
            title="⏰ Reminder Set",
            description=f"I'll remind you about: {reminder_text}",
            color=hikari.Color(0xe74c3c)
        )
        embed.add_field("Time", f"In {time_minutes} minutes", inline=True)
        embed.add_field("Requested by", ctx.author.mention, inline=True)
        
        await ctx.respond(embed=embed)
        
        await asyncio.sleep(time_minutes * 60)
        
        reminder_embed = hikari.Embed(
            title="⏰ Reminder!",
            description=reminder_text,
            color=hikari.Color(0xe74c3c)
        )
        await ctx.author.send(embed=reminder_embed)