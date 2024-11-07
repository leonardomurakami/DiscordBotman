import lightbulb

from base.command import BaseCommand
from views.poll_view import PollView, PollButton


class PollCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "poll"
        self.description = "Create an interactive poll"
        self.help_text = "!poll <question> | <option1> | <option2> ... or /poll - Create an interactive poll with up to 5 options"

    def create_command(self) -> lightbulb.Command:
        @self.plugin.command
        @lightbulb.set_help(self.help_text)
        @lightbulb.option("options", "Options separated by |", type=str, required=True, modifier=lightbulb.OptionModifier.CONSUME_REST)
        @lightbulb.option("question", "Question to be polled", type=str, required=True)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd

    async def execute(self, ctx: lightbulb.Context) -> None:
        options = [opt.strip() for opt in ctx.options.options.split("|")]
        
        if len(options) < 2:
            await ctx.respond("Please provide a question and at least 2 options separated by |")
            return
        
        if len(options) > 6:
            await ctx.respond("Maximum 5 options are allowed!")
            return
        
        question = ctx.options.question
        choices = options
        
        view = PollView(question, choices)
        for idx, choice in enumerate(choices):
            view.add_item(PollButton(idx, choice))
        
        message = await ctx.respond(embed=view.build_embed(), components=view.build())
        
        ctx.app.d.miru.start_view(view)
        await view.wait()
        
        final_embed = view.build_embed()
        final_embed.set_footer(text=f"Poll ended - Total votes: {sum(len(voters) for voters in view.votes.values())}")
        
        try:
            await message.edit(embed=final_embed, components=[])
        except:
            pass