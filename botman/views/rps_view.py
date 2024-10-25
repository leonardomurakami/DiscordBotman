import hikari
import miru


class RPSView(miru.View):
    def __init__(self, author: hikari.User) -> None:
        super().__init__(timeout=60)
        self.author = author
        self.user_choice = None
        
    @miru.button(label="Rock", emoji="🪨", style=hikari.ButtonStyle.PRIMARY)
    async def rock_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        if ctx.user.id != self.author.id:
            await ctx.respond("This isn't your game!", flags=hikari.MessageFlag.EPHEMERAL)
            return
        self.user_choice = "rock"
        await self.handle_choice(ctx)

    @miru.button(label="Paper", emoji="📄", style=hikari.ButtonStyle.PRIMARY)
    async def paper_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        if ctx.user.id != self.author.id:
            await ctx.respond("This isn't your game!", flags=hikari.MessageFlag.EPHEMERAL)
            return
        self.user_choice = "paper"
        await self.handle_choice(ctx)

    @miru.button(label="Scissors", emoji="✂️", style=hikari.ButtonStyle.PRIMARY)
    async def scissors_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        if ctx.user.id != self.author.id:
            await ctx.respond("This isn't your game!", flags=hikari.MessageFlag.EPHEMERAL)
            return
        self.user_choice = "scissors"
        await self.handle_choice(ctx)

    async def handle_choice(self, ctx: miru.ViewContext) -> None:
        bot_choice = random.choice(["rock", "paper", "scissors"])
        
        # Determine winner
        if self.user_choice == bot_choice:
            result = "It's a tie!"
            color = 0xffff00
        elif (
            (self.user_choice == "rock" and bot_choice == "scissors") or
            (self.user_choice == "paper" and bot_choice == "rock") or
            (self.user_choice == "scissors" and bot_choice == "paper")
        ):
            result = "You win!"
            color = 0x00ff00
        else:
            result = "I win!"
            color = 0xff0000
            
        # Create result embed
        result_embed = hikari.Embed(
            title="Rock, Paper, Scissors - Result",
            color=hikari.Color(color)
        )
        
        # Add emoji to choices
        choice_emojis = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
        user_choice_display = f"{choice_emojis[self.user_choice]} {self.user_choice.title()}"
        bot_choice_display = f"{choice_emojis[bot_choice]} {bot_choice.title()}"
        
        result_embed.add_field("Your Choice", user_choice_display, inline=True)
        result_embed.add_field("My Choice", bot_choice_display, inline=True)
        result_embed.add_field("Result", result, inline=False)
        
        await ctx.edit_response(embed=result_embed, components=[])
        self.stop()