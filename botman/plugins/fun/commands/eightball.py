import lightbulb
import hikari
import random

from base.command import BaseCommand


class Magic8BallCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "8ball"
        self.description = "Ask the magic 8-ball"
        self.help_text = "!8ball <question> or /8ball <question> - Ask the magic 8-ball a question"
        
    def create_command(self) -> lightbulb.Command:
        @self.plugin.command
        @lightbulb.set_help(self.help_text)
        @lightbulb.option("question", "The question to ask", type=str, required=True)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd

    async def execute(self, ctx: lightbulb.Context) -> None:
        responses = [
            "It is certain.", "Without a doubt.", "Yes, definitely.",
            "You may rely on it.", "As I see it, yes.", "Most likely.",
            "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
            "Cannot predict now.", "Don't count on it.", "My sources say no.",
            "Very doubtful.", "My reply is no.", "Outlook not so good."
        ]
        
        embed = hikari.Embed(
            title="🎱 Magic 8-Ball",
            color=hikari.Color(0x000000)
        )
        embed.add_field("Question", ctx.options.question, inline=False)
        embed.add_field("Answer", random.choice(responses), inline=False)
        
        await ctx.respond(embed=embed)