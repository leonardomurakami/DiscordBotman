import lightbulb
import hikari
import time

from base.command import BaseCommand


class PingCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "ping"
        self.description = "Check the bot's latency"
        self.help_text = "!ping or /ping - Shows the bot's latency to Discord's servers"

    def create_command(self) -> lightbulb.Command:
        @self.plugin.command
        @lightbulb.set_help(self.help_text)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd

    async def execute(self, ctx: lightbulb.Context) -> None:
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