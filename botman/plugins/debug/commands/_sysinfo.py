import lightbulb
import hikari
import platform
import psutil

from base.command import BaseCommand


class SysInfoCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "sysinfo"
        self.description = "Get system information"
        self.help_text = "!sysinfo or /sysinfo - Displays system information including CPU, RAM, and Python version"

    def create_command(self) -> lightbulb.Command:
        @self.plugin.command
        @lightbulb.set_help(self.help_text)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd

    async def execute(self, ctx: lightbulb.Context) -> None:
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