import lightbulb
import hikari
import datetime

plugin = lightbulb.Plugin("admin")
plugin.description = "Administrative commands for server management"

@plugin.command
@lightbulb.set_help("!kick <user> <reason> or /kick <user> <reason> - Kicks a user from the server")
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.KICK_MEMBERS))
@lightbulb.option("reason", "Reason for the kick", type=str, required=False, default="No reason provided")
@lightbulb.option("user", "The user to kick", type=hikari.User, required=True)
@lightbulb.command("kick", "Kick a user from the server")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def kick(ctx: lightbulb.Context) -> None:
    target = ctx.options.user
    reason = ctx.options.reason
    
    try:
        await ctx.get_guild().kick(target, reason=f"Kicked by {ctx.author}: {reason}")
        embed = hikari.Embed(
            title="User Kicked",
            description=f"Successfully kicked {target.mention}",
            color=hikari.Color(0xff9900)
        )
        embed.add_field("Reason", reason)
        await ctx.respond(embed=embed)
    except Exception as e:
        await ctx.respond(f"Failed to kick user: {str(e)}")

@plugin.command
@lightbulb.set_help("!ban <user> <reason> or /ban <user> <reason> - Bans a user from the server")
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.BAN_MEMBERS))
@lightbulb.option("reason", "Reason for the ban", type=str, required=False, default="No reason provided")
@lightbulb.option("user", "The user to ban", type=hikari.User, required=True)
@lightbulb.command("ban", "Ban a user from the server")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def ban(ctx: lightbulb.Context) -> None:
    target = ctx.options.user
    reason = ctx.options.reason
    
    try:
        await ctx.get_guild().ban(target, reason=f"Banned by {ctx.author}: {reason}")
        embed = hikari.Embed(
            title="User Banned",
            description=f"Successfully banned {target.mention}",
            color=hikari.Color(0xff0000)
        )
        embed.add_field("Reason", reason)
        await ctx.respond(embed=embed)
    except Exception as e:
        await ctx.respond(f"Failed to ban user: {str(e)}")

@plugin.command
@lightbulb.set_help("!purge <amount> or /purge <amount> - Deletes specified number of messages")
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_MESSAGES))
@lightbulb.option("amount", "Number of messages to delete", type=int, required=True)
@lightbulb.command("purge", "Delete multiple messages")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def purge(ctx: lightbulb.Context) -> None:
    amount = min(max(1, ctx.options.amount), 100)  # Limit between 1 and 100
    
    try:
        messages = (
            await ctx.bot.rest.fetch_messages(ctx.channel_id)
            .take_until(lambda m: datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=14) > m.created_at)
            .limit(amount)
        )
        await ctx.get_channel().delete_messages(messages)
        
        embed = hikari.Embed(
            title="Messages Purged",
            description=f"Successfully deleted {len(messages)} messages",
            color=hikari.Color(0x00ff00)
        )
        await ctx.respond(embed=embed, delete_after=5)
    except Exception as e:
        await ctx.respond(f"Failed to purge messages: {str(e)}")

@plugin.command
@lightbulb.set_help("!mute <user> <duration> <reason> or /mute <user> <duration> <reason> - Timeout a user")
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MODERATE_MEMBERS))
@lightbulb.option("reason", "Reason for the mute", type=str, required=False, default="No reason provided")
@lightbulb.option("duration", "Duration in minutes", type=int, required=True)
@lightbulb.option("user", "The user to mute", type=hikari.User, required=True)
@lightbulb.command("mute", "Timeout a user")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def mute(ctx: lightbulb.Context) -> None:
    target = ctx.options.user
    duration = ctx.options.duration
    reason = ctx.options.reason
    
    try:
        until = datetime.datetime.now() + datetime.timedelta(minutes=duration)
        await ctx.get_guild().edit_member(target, communication_disabled_until=until)
        
        embed = hikari.Embed(
            title="User Muted",
            description=f"Successfully muted {target.mention}",
            color=hikari.Color(0xff6600)
        )
        embed.add_field("Duration", f"{duration} minutes")
        embed.add_field("Reason", reason)
        await ctx.respond(embed=embed)
    except Exception as e:
        await ctx.respond(f"Failed to mute user: {str(e)}")

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)

def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(plugin)