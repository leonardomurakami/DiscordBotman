import lightbulb
import hikari

from datetime import datetime

plugin = lightbulb.Plugin("moderation")
plugin.description = "Advanced moderation commands for server management"

@plugin.command
@lightbulb.set_help("!slowmode <duration> or /slowmode - Set channel slowmode (0 to disable)")
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_CHANNELS))
@lightbulb.option("duration", "Slowmode duration in seconds (0 to disable)", type=int, required=True)
@lightbulb.command("slowmode", "Set channel slowmode")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def slowmode(ctx: lightbulb.Context) -> None:
    duration = max(0, min(ctx.options.duration, 21600))  # Limit to Discord's max of 6 hours
    
    try:
        await ctx.get_channel().edit(rate_limit_per_user=duration)
        
        if duration == 0:
            description = "Slowmode has been disabled"
        else:
            description = f"Slowmode set to {duration} seconds"
            
        embed = hikari.Embed(
            title="Slowmode Updated",
            description=description,
            color=hikari.Color(0x2ecc71)
        )
        await ctx.respond(embed=embed)
    except Exception as e:
        await ctx.respond(f"Failed to set slowmode: {str(e)}")

@plugin.command
@lightbulb.set_help("!warn <user> <reason> or /warn - Warn a user")
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MODERATE_MEMBERS))
@lightbulb.option("reason", "Reason for the warning", type=str, required=True)
@lightbulb.option("user", "The user to warn", type=hikari.User, required=True)
@lightbulb.command("warn", "Warn a user")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def warn(ctx: lightbulb.Context) -> None:
    target = ctx.options.user
    reason = ctx.options.reason
    
    # Store warning in bot's memory (could be extended to use a database)
    if not hasattr(ctx.bot, 'warnings'):
        ctx.bot.warnings = {}
    
    if ctx.guild_id not in ctx.bot.warnings:
        ctx.bot.warnings[ctx.guild_id] = {}
    
    if target.id not in ctx.bot.warnings[ctx.guild_id]:
        ctx.bot.warnings[ctx.guild_id][target.id] = []
    
    ctx.bot.warnings[ctx.guild_id][target.id].append({
        'reason': reason,
        'mod': ctx.author.id,
        'time': datetime.now()
    })
    
    embed = hikari.Embed(
        title="User Warned",
        description=f"{target.mention} has been warned",
        color=hikari.Color(0xff9900)
    )
    embed.add_field("Reason", reason)
    embed.add_field("Total Warnings", str(len(ctx.bot.warnings[ctx.guild_id][target.id])))
    
    await ctx.respond(embed=embed)
    
    try:
        # DM the user
        user_embed = hikari.Embed(
            title="Warning Received",
            description=f"You have been warned in {ctx.get_guild().name}",
            color=hikari.Color(0xff9900)
        )
        user_embed.add_field("Reason", reason)
        await target.send(embed=user_embed)
    except:
        await ctx.respond("Note: Could not DM user about the warning.")

@plugin.command
@lightbulb.set_help("!warnings <user> or /warnings - Check a user's warnings")
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MODERATE_MEMBERS))
@lightbulb.option("user", "The user to check", type=hikari.User, required=True)
@lightbulb.command("warnings", "Check a user's warnings")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def warnings(ctx: lightbulb.Context) -> None:
    target = ctx.options.user
    
    if not hasattr(ctx.bot, 'warnings') or \
       ctx.guild_id not in ctx.bot.warnings or \
       target.id not in ctx.bot.warnings[ctx.guild_id]:
        embed = hikari.Embed(
            title="User Warnings",
            description=f"{target.mention} has no warnings",
            color=hikari.Color(0x2ecc71)
        )
        await ctx.respond(embed=embed)
        return
    
    warnings = ctx.bot.warnings[ctx.guild_id][target.id]
    
    embed = hikari.Embed(
        title="User Warnings",
        description=f"{target.mention} has {len(warnings)} warning(s)",
        color=hikari.Color(0xff9900)
    )
    
    for idx, warning in enumerate(warnings, 1):
        mod = ctx.bot.cache.get_user(warning['mod'])
        mod_name = mod.username if mod else "Unknown Moderator"
        time_str = warning['time'].strftime("%Y-%m-%d %H:%M:%S")
        
        embed.add_field(
            name=f"Warning {idx}",
            value=f"**Reason:** {warning['reason']}\n"
                  f"**Moderator:** {mod_name}\n"
                  f"**Time:** {time_str}",
            inline=False
        )
    
    await ctx.respond(embed=embed)

@plugin.command
@lightbulb.set_help("!clearwarnings <user> or /clearwarnings - Clear all warnings for a user")
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MODERATE_MEMBERS))
@lightbulb.option("user", "The user to clear warnings for", type=hikari.User, required=True)
@lightbulb.command("clearwarnings", "Clear all warnings for a user")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def clearwarnings(ctx: lightbulb.Context) -> None:
    target = ctx.options.user
    
    if not hasattr(ctx.bot, 'warnings') or \
       ctx.guild_id not in ctx.bot.warnings or \
       target.id not in ctx.bot.warnings[ctx.guild_id]:
        await ctx.respond(f"{target.mention} has no warnings to clear.")
        return
    
    warning_count = len(ctx.bot.warnings[ctx.guild_id][target.id])
    del ctx.bot.warnings[ctx.guild_id][target.id]
    
    embed = hikari.Embed(
        title="Warnings Cleared",
        description=f"Cleared {warning_count} warning(s) for {target.mention}",
        color=hikari.Color(0x2ecc71)
    )
    await ctx.respond(embed=embed)

@plugin.command
@lightbulb.set_help("!lock or /lock - Lock the current channel")
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_CHANNELS))
@lightbulb.option("reason", "Reason for locking the channel", type=str, required=False, default="No reason provided")
@lightbulb.command("lock", "Lock the current channel")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def lock(ctx: lightbulb.Context) -> None:
    channel = ctx.get_channel()
    everyone_role = ctx.get_guild().get_role(ctx.guild_id)
    
    try:
        await ctx.bot.rest.edit_permission_overwrite(
            channel=channel.id,
            target=everyone_role,
            allow=0,
            deny=hikari.Permissions.SEND_MESSAGES,
            reason=ctx.options.reason
        )
        
        embed = hikari.Embed(
            title="Channel Locked",
            description=f"🔒 This channel has been locked\nReason: {ctx.options.reason}",
            color=hikari.Color(0xe74c3c)
        )
        await ctx.respond(embed=embed)
    except Exception as e:
        await ctx.respond(f"Failed to lock channel: {str(e)}")

@plugin.command
@lightbulb.set_help("!unlock or /unlock - Unlock the current channel")
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_CHANNELS))
@lightbulb.command("unlock", "Unlock the current channel")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def unlock(ctx: lightbulb.Context) -> None:
    channel = ctx.get_channel()
    everyone_role = ctx.get_guild().get_role(ctx.guild_id)
    
    try:
        await ctx.bot.rest.edit_permission_overwrite(
            channel=channel.id,
            target=everyone_role,
            allow=hikari.Permissions.SEND_MESSAGES
        )
        
        embed = hikari.Embed(
            title="Channel Unlocked",
            description="🔓 This channel has been unlocked",
            color=hikari.Color(0x2ecc71)
        )
        await ctx.respond(embed=embed)

    except Exception as e:
        await ctx.respond(f"Failed to unlock channel: {str(e)}")

@plugin.command
@lightbulb.set_help("!roleinfo <role> or /roleinfo - Display information about a role")
@lightbulb.option("role", "The role to get information about", type=hikari.Role, required=True)
@lightbulb.command("roleinfo", "Get information about a role")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def roleinfo(ctx: lightbulb.Context) -> None:
    role = ctx.options.role
    guild = ctx.get_guild()
    
    # Count members with this role
    member_count = len([m for m in guild.get_members().values() if role.id in m.role_ids])
    
    embed = hikari.Embed(
        title=f"Role Information: {role.name}",
        color=role.color
    )
    
    embed.add_field("ID", str(role.id), inline=True)
    embed.add_field("Members", str(member_count), inline=True)
    embed.add_field("Color", str(role.color), inline=True)
    embed.add_field("Mentionable", "Yes" if role.is_mentionable else "No", inline=True)
    embed.add_field("Hoisted", "Yes" if role.is_hoisted else "No", inline=True)
    embed.add_field("Position", str(role.position), inline=True)
    embed.add_field("Created", f"<t:{int(role.created_at.timestamp())}:R>", inline=True)
    
    # Add key permissions
    key_perms = []
    if role.permissions & hikari.Permissions.ADMINISTRATOR:
        key_perms.append("Administrator")
    if role.permissions & hikari.Permissions.MANAGE_GUILD:
        key_perms.append("Manage Server")
    if role.permissions & hikari.Permissions.MANAGE_CHANNELS:
        key_perms.append("Manage Channels")
    if role.permissions & hikari.Permissions.MANAGE_ROLES:
        key_perms.append("Manage Roles")
    if role.permissions & hikari.Permissions.MANAGE_MESSAGES:
        key_perms.append("Manage Messages")
    if role.permissions & hikari.Permissions.KICK_MEMBERS:
        key_perms.append("Kick Members")
    if role.permissions & hikari.Permissions.BAN_MEMBERS:
        key_perms.append("Ban Members")
    
    if key_perms:
        embed.add_field("Key Permissions", ", ".join(key_perms), inline=False)
    
    await ctx.respond(embed=embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)

def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(plugin)