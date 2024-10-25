import lightbulb
import hikari
import platform
import psutil
import time
import asyncio

plugin = lightbulb.Plugin("debug")
plugin.description = "Debug and system information commands"

@plugin.command
@lightbulb.set_help("!hello or /hello - Simple greeting command to test if the bot is responsive", )
@lightbulb.command("hello", "Says hello to the user")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def hello(ctx: lightbulb.Context) -> None:
    await ctx.respond(f"Hello, {ctx.author.mention}!")

@plugin.command
@lightbulb.set_help("!ping or /ping - Shows the bot's latency to Discord's servers")
@lightbulb.command("ping", "Check the bot's latency")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def ping(ctx: lightbulb.Context) -> None:
    start_time = time.perf_counter()
    message = await ctx.respond("Pinging...")
    end_time = time.perf_counter()
    
    latency = (end_time - start_time) * 1000
    heartbeat = ctx.bot.heartbeat_latency * 1000

    embed = hikari.Embed(
        title="🏓 Pong!",
        color=hikari.Color(0x3498db)
    )
    embed.add_field("API Latency", f"`{latency:.2f}ms`", inline=True)
    embed.add_field("Heartbeat Latency", f"`{heartbeat:.2f}ms`", inline=True)
    
    await message.edit(content=None, embed=embed)

@plugin.command
@lightbulb.set_help("!sysinfo or /sysinfo - Displays system information including CPU, RAM, and Python version")
@lightbulb.command("sysinfo", "Get system information")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def sysinfo(ctx: lightbulb.Context) -> None:
    # Get system information
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    embed = hikari.Embed(
        title="System Information",
        color=hikari.Color(0x3498db)
    )
    
    embed.add_field(
        name="System",
        value=f"```\nOS: {platform.system()} {platform.release()}\n"
              f"Python: {platform.python_version()}\n"
              f"Hikari: {hikari.__version__}\n"
              f"Lightbulb: {lightbulb.__version__}```",
        inline=False
    )
    
    embed.add_field(
        name="CPU",
        value=f"```\nUsage: {cpu_percent}%```",
        inline=True
    )
    
    embed.add_field(
        name="Memory",
        value=f"```\nTotal: {memory.total // (1024**3)}GB\n"
              f"Used: {memory.used // (1024**3)}GB\n"
              f"Free: {memory.available // (1024**3)}GB```",
        inline=True
    )
    
    embed.add_field(
        name="Disk",
        value=f"```\nTotal: {disk.total // (1024**3)}GB\n"
              f"Used: {disk.used // (1024**3)}GB\n"
              f"Free: {disk.free // (1024**3)}GB```",
        inline=True
    )
    
    await ctx.respond(embed=embed)

@lightbulb.add_checks(lightbulb.owner_only)
@plugin.command
@lightbulb.set_help("!eval <code> or /eval <code> - Evaluates Python code (Owner only for security)")
@lightbulb.option("code", "The Python code to evaluate", type=str, required=True)
@lightbulb.command("eval", "Evaluate Python code (Owner only)")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def eval_code(ctx: lightbulb.Context) -> None:
    code = ctx.options.code
    try:
        # Add some common imports that might be useful
        globals_dict = {
            'ctx': ctx,
            'bot': ctx.bot,
            'hikari': hikari,
            'lightbulb': lightbulb,
            'plugin': plugin
        }
        
        # Execute the code
        result = eval(code, globals_dict)
        
        if asyncio.iscoroutine(result):
            result = await result
            
        embed = hikari.Embed(
            title="Code Evaluation",
            color=hikari.Color(0x2ecc71)
        )
        embed.add_field(
            name="Input",
            value=f"```python\n{code}```",
            inline=False
        )
        embed.add_field(
            name="Output",
            value=f"```python\n{result}```",
            inline=False
        )
        
        await ctx.respond(embed=embed)
        
    except Exception as e:
        embed = hikari.Embed(
            title="Code Evaluation Error",
            color=hikari.Color(0xe74c3c)
        )
        embed.add_field(
            name="Input",
            value=f"```python\n{code}```",
            inline=False
        )
        embed.add_field(
            name="Error",
            value=f"```python\n{type(e).__name__}: {str(e)}```",
            inline=False
        )
        
        await ctx.respond(embed=embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)

def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(plugin)