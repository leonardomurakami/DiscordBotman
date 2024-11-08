from typing import Union
import hikari
import lightbulb
import logging
from base.plugin import BasePlugin
from base.command import BaseCommand
from views.help_view import HelpView

logger = logging.getLogger(__name__)

class HelpCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "help"
        self.description = "Shows help information about commands and plugins"
        self.help_text = "!help [command|plugin] or /help [command|plugin] - Shows help information"

    def create_command(self) -> lightbulb.Command:
        @self.plugin.command
        @lightbulb.set_help(self.help_text)
        @lightbulb.option("query", "Command or plugin to get help for", type=str, required=False)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd

    async def execute(self, ctx: lightbulb.Context) -> None:
        query = ctx.options.query if hasattr(ctx.options, 'query') else None
        
        if not query:
            await self._send_bot_help(ctx)
        else:
            # Try to find the command or plugin
            command = ctx.bot.get_slash_command(query)
            plugin = ctx.bot.get_plugin(query)
            
            if command:
                await self._send_command_help(ctx, command)
            elif plugin:
                await self._send_plugin_help(ctx, plugin)
            else:
                await self._object_not_found(ctx, query)

    async def _send_bot_help(self, ctx: lightbulb.Context) -> None:
        embeds = []
        labels = []

        # Create overview embed
        overview = hikari.Embed(
            title="Bot Help Overview",
            description="Welcome to the help menu! Navigate through pages to see all commands.",
            color=hikari.Color(0x3498db)
        )
        overview.add_field(
            name="How to use",
            value=(
                "• Use `/help` to see this overview\n"
                "• Use `/help <command>` to get detailed help for a command\n"
                "• Use `/help <plugin>` to see all commands in a plugin"
            ),
            inline=False
        )
        embeds.append(overview)
        labels.append("Overview")

        # Create an embed for each plugin
        for plugin in ctx.bot.plugins.values():
            if not plugin.all_commands:
                continue

            embed = hikari.Embed(
                title=f"{plugin.name} Plugin",
                description=plugin.description or "No description provided",
                color=hikari.Color(0x3498db)
            )

            # Only show slash commands
            commands = [cmd for cmd in plugin.all_commands 
                       if not isinstance(cmd, lightbulb.commands.prefix.PrefixCommand)]
            
            if commands:
                command_list = []
                for cmd in commands:
                    command_list.append(
                        f"**{cmd.name}**\n"
                        f"└ {cmd.description}\n"
                        f"└ Usage: {cmd.signature}"
                    )
                embed.add_field(
                    name="Available Commands",
                    value="\n".join(command_list) if command_list else "No commands available",
                    inline=False
                )
                
                embeds.append(embed)
                labels.append(plugin.name)

        # Send embeds with navigation
        view = HelpView(embeds, labels, timeout=300.0)
        response = await ctx.respond(embed=embeds[0], components=view.build())
        message = await response.message()
        ctx.app.d.miru.start_view(view)

    async def _send_plugin_help(self, ctx: lightbulb.Context, plugin: lightbulb.Plugin) -> None:
        embed = hikari.Embed(
            title=f"{plugin.name} Plugin",
            description=plugin.description or "No description provided",
            color=hikari.Color(0x3498db)
        )

        commands = [cmd for cmd in plugin.all_commands 
                   if not isinstance(cmd, lightbulb.commands.prefix.PrefixCommand)]
        
        if commands:
            command_list = []
            for cmd in commands:
                command_list.append(
                    f"**{cmd.name}**\n"
                    f"└ {cmd.description}\n"
                    f"└ Usage: {cmd.signature}"
                )
            embed.add_field(
                name="Available Commands",
                value="\n".join(command_list),
                inline=False
            )
        else:
            embed.add_field(
                name="Commands",
                value="No commands available",
                inline=False
            )

        await ctx.respond(embed=embed)

    async def _send_command_help(self, ctx: lightbulb.Context, command: lightbulb.Command) -> None:
        embed = hikari.Embed(
            title=f"Command: {command.name}",
            description=command.description,
            color=hikari.Color(0x3498db)
        )

        # Add command usage
        embed.add_field(
            name="Usage",
            value=command.signature,
            inline=False
        )

        # Add command options
        if hasattr(command, "options"):
            options_text = []
            for opt in command.options:
                opt_text = f"**{opt.name}** - {opt.description}"
                if opt.required:
                    opt_text += " *(required)*"
                options_text.append(opt_text)
            
            if options_text:
                embed.add_field(
                    name="Options",
                    value="\n".join(options_text),
                    inline=False
                )

        # Add permissions if any
        if hasattr(command, "checks"):
            perms = []
            for check in command.checks:
                if isinstance(check, lightbulb.checks.has_guild_permissions):
                    perms.extend(str(perm).replace('_', ' ').title() for perm in check.perms)
            
            if perms:
                embed.add_field(
                    name="Required Permissions",
                    value="\n".join(perms),
                    inline=False
                )

        await ctx.respond(embed=embed)

    async def _object_not_found(self, ctx: lightbulb.Context, obj: str) -> None:
        embed = hikari.Embed(
            title="Not Found",
            description=f"No command or plugin found matching '{obj}'",
            color=hikari.Color(0xff0000)
        )
        await ctx.respond(embed=embed)

class HelpPlugin(BasePlugin):
    @property
    def plugin_name(self) -> str:
        return "help"
        
    @property
    def plugin_description(self) -> str:
        return "Help and documentation for bot commands"
        
    def _setup_commands(self) -> None:
        self.commands = [
            HelpCommand(self.plugin)
        ]

def load(bot: lightbulb.BotApp) -> None:
    plugin = HelpPlugin(bot)
    plugin.load()

def unload(bot: lightbulb.BotApp) -> None:
    plugin = HelpPlugin(bot)
    plugin.unload()