import lightbulb
import hikari
import random
import string
import asyncio
import logging
import datetime

import config

from views.poll_view import PollView, PollButton


plugin = lightbulb.Plugin("utility")
plugin.description = "Utility commands for server management and information"
logger = logging.getLogger(__name__)

@plugin.command
@lightbulb.set_help("!userinfo <user> or /userinfo <user> - Shows detailed information about a user")
@lightbulb.option("user", "The user to get information about", type=hikari.User, required=False)
@lightbulb.command("userinfo", "Get detailed information about a user")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def userinfo(ctx: lightbulb.Context) -> None:
    target = ctx.options.user or ctx.author
    member = ctx.get_guild().get_member(target.id)
    
    roles = [role.mention for role in member.get_roles()] if member else []
    roles_str = ", ".join(roles) if roles else "No roles"
    
    embed = hikari.Embed(
        title="User Information",
        color=hikari.Color(0x3498db)
    )
    
    embed.set_thumbnail(target.avatar_url)
    embed.add_field("Username", str(target), inline=True)
    embed.add_field("ID", str(target.id), inline=True)
    embed.add_field("Bot", "Yes" if target.is_bot else "No", inline=True)
    embed.add_field("Account Created", f"<t:{int(target.created_at.timestamp())}:R>", inline=True)
    
    if member:
        embed.add_field("Joined Server", f"<t:{int(member.joined_at.timestamp())}:R>", inline=True)
        embed.add_field("Roles", roles_str, inline=False)
    
    await ctx.respond(embed=embed)

@plugin.command
@lightbulb.set_help("!serverinfo or /serverinfo - Shows detailed information about the server")
@lightbulb.command("serverinfo", "Get detailed information about the server")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def serverinfo(ctx: lightbulb.Context) -> None:
    guild = ctx.get_guild()
    
    embed = hikari.Embed(
        title=f"{guild.name} - Server Information",
        color=hikari.Color(0x2ecc71)
    )
    
    if guild.icon_url:
        embed.set_thumbnail(guild.icon_url)
    
    embed.add_field("Owner", f"<@{guild.owner_id}>", inline=True)
    embed.add_field("Created", f"<t:{int(guild.created_at.timestamp())}:R>", inline=True)
    embed.add_field("Members", str(guild.member_count), inline=True)
    embed.add_field("Channels", str(len(guild.get_channels())), inline=True)
    embed.add_field("Roles", str(len(guild.get_roles())), inline=True)
    embed.add_field("Boost Level", str(guild.premium_tier), inline=True)
    
    await ctx.respond(embed=embed)

@plugin.command
@lightbulb.set_help("!poll <question> | <option1> | <option2> ... or /poll - Create an interactive poll with up to 5 options")
@lightbulb.option("options", "Options separated by |", type=str, required=True, modifier=lightbulb.OptionModifier.CONSUME_REST)
@lightbulb.option("question", "Question to be polled", type=str, required=True)
@lightbulb.command("poll", "Create an interactive poll")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def poll(ctx: lightbulb.Context) -> None:
    options = [opt.strip() for opt in ctx.options.options.split("|")]
    logger.info(options)

    
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

@plugin.command
@lightbulb.set_help("!remind <time> <reminder> or /remind - Set a reminder (time in minutes)")
@lightbulb.option("reminder", "What to remind you about", type=str, required=True)
@lightbulb.option("time", "Time in minutes", type=int, required=True)
@lightbulb.command("remind", "Set a reminder")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def remind(ctx: lightbulb.Context) -> None:
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

@plugin.command
@lightbulb.set_help("!password <length> or /password - Generate a secure random password")
@lightbulb.option("length", "Password length", type=int, required=False, default=16)
@lightbulb.command("password", "Generate a secure random password")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def password(ctx: lightbulb.Context) -> None:
    length = max(8, min(ctx.options.length, 32))  # Limit between 8 and 32
    
    # Define character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special = "!@#$%^&*"
    
    # Ensure at least one character from each set
    password = [
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(digits),
        random.choice(special)
    ]
    
    # Fill the rest randomly
    all_chars = lowercase + uppercase + digits + special
    password.extend(random.choice(all_chars) for _ in range(length - 4))
    
    # Shuffle the password
    random.shuffle(password)
    password_str = "".join(password)
    
    # Send password in ephemeral message
    embed = hikari.Embed(
        title="🔒 Password Generated",
        description=f"||`{password_str}`||",
        color=hikari.Color(0x1abc9c)
    )
    embed.add_field("Length", str(length), inline=True)
    embed.set_footer(text="This message will be automatically deleted in 1 minute.\nThis bot will never store the generated passwords.")
    
    await ctx.respond(embed=embed, flags=hikari.MessageFlag.EPHEMERAL, delete_after=60)

@plugin.command
@lightbulb.set_help("!snipe or /snipe - Shows the last deleted message in the channel")
@lightbulb.command("snipe", "Show the last deleted message")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def snipe(ctx: lightbulb.Context) -> None:
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
    
    # Add attachment info if present
    if deleted['attachments']:
        attachment_names = [a.filename for a in deleted['attachments']]
        embed.add_field(
            name="📎 Attachments",
            value="\n".join(attachment_names),
            inline=False
        )
    
    embed.set_footer(text="Message deleted at")
    
    await ctx.respond(embed=embed)

@plugin.command
@lightbulb.set_help("!editsnipe or /editsnipe - Shows the last edited message in the channel")
@lightbulb.command("editsnipe", "Show the last edited message")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def editsnipe(ctx: lightbulb.Context) -> None:
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

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)

def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(plugin)