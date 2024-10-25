import os
import miru
import hikari
import logging
import datetime
import lightbulb
import traceback

from help import HelpCommand

bot = lightbulb.BotApp(
    token=os.getenv("DISCORD_BOT_TOKEN", ""),
    prefix="!",
    help_class=HelpCommand,
    intents=hikari.Intents.ALL,
    owner_ids=[int(os.getenv("DISCORD_BOT_OWNER_ID", "0"))]
)
bot.d.miru = miru.Client(bot)
bot.d.deleted_messages = {}
bot.d.edited_messages = {}

logger = logging.getLogger(__name__)
# Load command modules
bot.load_extensions_from("./commands")

@bot.listen(hikari.StartedEvent)
async def on_started(event):
    logger.info("Bot has started!")

@bot.listen(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    if isinstance(event.exception, lightbulb.CommandNotFound):
        # Handle command not found
        command = str(event.exception).split("'")[1]
        embed = hikari.Embed(
            title="❌ Command Not Found",
            description=f"""The command `{command}` doesn't exist!""",
            color=hikari.Color(0xff0000)
        )
        embed.add_field(
            name="Need Help?",
            value="Use `!help` to see a list of all available commands.",
            inline=False
        )
        logger.error(f"User {event.context.author.username} in guild {event.context.guild_id} ran unknown command: {command}")
        await event.context.respond(embed=embed)
        return

    if isinstance(event.exception, lightbulb.MissingRequiredPermission):
        # Handle missing permissions
        embed = hikari.Embed(
            title="❌ Missing Permissions",
            description="You don't have the required permissions to use this command!",
            color=hikari.Color(0xff0000)
        )
        await event.context.respond(embed=embed)
        return

    if isinstance(event.exception, lightbulb.NotOwner):
        # Handle non-owner using owner-only commands
        embed = hikari.Embed(
            title="❌ Owner Only",
            description="This command can only be used by the bot owner!",
            color=hikari.Color(0xff0000)
        )
        await event.context.respond(embed=embed)
        return

    if isinstance(event.exception, lightbulb.CommandIsOnCooldown):
        # Handle cooldown
        embed = hikari.Embed(
            title="⏳ Cooldown",
            description=f"This command is on cooldown! Try again in {event.exception.retry_after:.2f} seconds.",
            color=hikari.Color(0xff9900)
        )
        await event.context.respond(embed=embed)
        return

    if isinstance(event.exception, lightbulb.NotEnoughArguments):
        # Handle missing arguments
        embed = hikari.Embed(
            title="❌ Missing Argument",
            description=f"Missing required argument: `{' '.join(options.name for options in event.exception.missing_options)}`",
            color=hikari.Color(0xff0000)
        )
        embed.add_field(
            name="Usage",
            value=f"`{event.context.prefix}{event.context.command.signature}`",
            inline=False
        )
        await event.context.respond(embed=embed)
        return

    if isinstance(event.exception, lightbulb.CommandInvocationError):
        # Handle general command errors
        embed = hikari.Embed(
            title="❌ Command Error",
            description="An error occurred while executing the command!",
            color=hikari.Color(0xff0000)
        )
        
        # Add error details if you want to show them
        error_details = ''.join(traceback.format_exception(
            type(event.exception.__cause__),
            event.exception.__cause__,
            event.exception.__cause__.__traceback__
        ))
        
        # Optionally add a simplified error message to the embed
        embed.add_field(
            name="Error Details",
            value=f"```{str(event.exception.__cause__)}```",
            inline=False
        )
        
        await event.context.respond(embed=embed)
        return

    # Handle any other unexpected errors
    embed = hikari.Embed(
        title="❌ Unexpected Error",
        description="An unexpected error occurred! Please try again later.",
        color=hikari.Color(0xff0000)
    )
    
    await event.context.respond(embed=embed)

@bot.listen(hikari.GuildMessageDeleteEvent)
async def on_message_delete(event: hikari.GuildMessageDeleteEvent) -> None:
    if not event.old_message:
        return
        
    if event.old_message.author.is_bot:
        return
    bot.d.deleted_messages[event.channel_id] = {
        'content': event.old_message.content,
        'author': event.old_message.author,
        'time': datetime.datetime.now(),
        'attachments': event.old_message.attachments
    }

@bot.listen(hikari.GuildMessageUpdateEvent)
async def on_message_edit(event: hikari.GuildMessageUpdateEvent) -> None:
    if not event.old_message:
        return
        
    if event.old_message.author.is_bot:
        return
    
    bot.d.edited_messages[event.channel_id] = {
        'old_content': event.old_message.content,
        'new_content': event.message.content,
        'author': event.old_message.author,
        'time': datetime.datetime.now()
    }

bot.run()