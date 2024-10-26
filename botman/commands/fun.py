import lightbulb
import hikari
import random
import asyncio

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
        
@plugin.command
@lightbulb.set_help("!wake <user> or /wake <user> - Moves a user between voice channels briefly to get their attention")
@lightbulb.option("user", "The user to wake up", type=hikari.Member, required=True)
@lightbulb.option("times", "Number of moves (default: 5, max: 10)", type=int, required=False, default=5)
@lightbulb.command("wake", "Wake up a user in voice chat")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def wake(ctx: lightbulb.Context) -> None:
    target_user = ctx.options.user
    target_user_voicestate = ctx.bot.cache.get_voice_state(ctx.guild_id, target_user.id)
    times = min(max(1, ctx.options.times), 10)
    
    # Check if the target user is in a voice channel
    if not target_user_voicestate:
        embed = hikari.Embed(
            title="Error",
            description=f"{target_user.mention} is not in a voice channel!",
            color=hikari.Color(0xff0000)
        )
        await ctx.respond(embed=embed)
        return

    # Get current voice channel
    original_channel = target_user_voicestate.channel_id
    
    # Get available voice channels the user has access to
    guild = ctx.get_guild()
    available_channels = []
    
    for channel in guild.get_channels().values():
        if isinstance(channel, hikari.GuildVoiceChannel):
            # Check if channel is empty and user has access
            member_count = len(ctx.bot.cache.get_voice_states_view_for_channel(
                ctx.guild_id,
                channel.id
            ))
            
            if member_count == 0 or (member_count == 1 and target_user_voicestate.channel_id == channel.id):
                # Check permissions
                permissions = lightbulb.utils.permissions_in(channel, target_user)
                if permissions & hikari.Permissions.CONNECT:
                    available_channels.append(channel.id)
    
    if len(available_channels) < 2:
        embed = hikari.Embed(
            title="Error",
            description="Not enough available voice channels to perform the wake command!",
            color=hikari.Color(0xff0000)
        )
        await ctx.respond(embed=embed)
        return
    
    embed = hikari.Embed(
        title="Wake Command",
        description=f"Waking up {target_user.mention}...",
        color=hikari.Color(0x3498db)
    )
    await ctx.respond(embed=embed)
    
    # Move user between random channels
    try:
        for i in range(times):
            # Remove current channel from available channels for next move
            current_channel = target_user_voicestate.channel_id
            temp_channels = [c for c in available_channels if c != current_channel]
            
            if not temp_channels:  # If somehow we run out of channels
                break
                
            # Move to a random available channel
            next_channel = random.choice(temp_channels)
            await target_user.edit(voice_channel=next_channel)
            await asyncio.sleep(0.5)  # Wait half a second
        
        # Finally, return to original channel
        await target_user.edit(voice_channel=original_channel)
            
        embed = hikari.Embed(
            title="Wake Command",
            description=f"Successfully woke up {target_user.mention}!",
            color=hikari.Color(0x00ff00)
        )
        await ctx.edit_last_response(embed=embed)
            
    except hikari.ForbiddenError:
        embed = hikari.Embed(
            title="Error",
            description="I don't have permission to move that user!",
            color=hikari.Color(0xff0000)
        )
        await ctx.edit_last_response(embed=embed)
    except Exception as e:
        embed = hikari.Embed(
            title="Error",
            description=f"An error occurred: {str(e)}",
            color=hikari.Color(0xff0000)
        )
        await ctx.edit_last_response(embed=embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)

def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(plugin)