import lightbulb
import hikari
import random

from views.rps_view import RPSView

plugin = lightbulb.Plugin("fun")
plugin.description = "Fun and entertainment commands"


@plugin.command
@lightbulb.set_help("!flip or /flip - Flips a coin")
@lightbulb.command("flip", "Flip a coin")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def flip(ctx: lightbulb.Context) -> None:
    result = random.choice(["Heads", "Tails"])
    embed = hikari.Embed(
        title="Coin Flip",
        description=f"🪙 The coin landed on **{result}**!",
        color=hikari.Color(0xffd700)
    )
    await ctx.respond(embed=embed)

@plugin.command
@lightbulb.set_help("!roll <sides> or /roll <sides> - Rolls a dice with specified number of sides")
@lightbulb.option("sides", "Number of sides on the dice", type=int, default=6)
@lightbulb.command("roll", "Roll a dice")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def roll(ctx: lightbulb.Context) -> None:
    sides = max(2, ctx.options.sides)  # Ensure at least 2 sides
    result = random.randint(1, sides)
    embed = hikari.Embed(
        title="Dice Roll",
        description=f"🎲 You rolled a **{result}** (d{sides})!",
        color=hikari.Color(0xff4500)
    )
    await ctx.respond(embed=embed)

@plugin.command
@lightbulb.set_help("!8ball <question> or /8ball <question> - Ask the magic 8-ball a question")
@lightbulb.option("question", "The question to ask", type=str, required=True)
@lightbulb.command("8ball", "Ask the magic 8-ball")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def magic_8ball(ctx: lightbulb.Context) -> None:
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

@plugin.command
@lightbulb.set_help("!rps or /rps - Play Rock, Paper, Scissors using buttons")
@lightbulb.command("rps", "Play Rock, Paper, Scissors")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def rps(ctx: lightbulb.Context) -> None:
    embed = hikari.Embed(
        title="Rock, Paper, Scissors",
        description="Choose your move!",
        color=hikari.Color(0x3498db)
    )
    embed.add_field(
        name="How to Play",
        value="• Click a button to make your move\n"
              "• Rock beats Scissors\n"
              "• Paper beats Rock\n"
              "• Scissors beats Paper",
        inline=False
    )
    
    view = RPSView(ctx.author)
    message = await ctx.respond(embed=embed, components=view.build())
    
    ctx.app.d.miru.start_view(view)
    await view.wait()
    
    if view.user_choice is None:
        embed.description = "Game timed out! Please try again."
        await message.edit(embed=embed, components=[])

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)

def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(plugin)