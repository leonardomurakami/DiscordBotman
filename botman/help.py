import lightbulb
import hikari
import logging
from typing import Union
from views.help_view import HelpView

logger = logging.getLogger(__name__)

class HelpCommand(lightbulb.BaseHelpCommand):
    async def send_bot_help(self, context: lightbulb.Context) -> None:
        embeds = []
        labels = []

        # Create an overview embed
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


        for plugin in context.bot.plugins.values():
            logger.info(f"All commands: {plugin.all_commands}")  # Debug log
            if not plugin.all_commands:
                continue
                
            logger.info(f"Processing plugin: {plugin.name}")  # Debug log

            embed = hikari.Embed(
                title=f"{plugin.name} Plugin",
                description=plugin.description or "No description provided",
                color=hikari.Color(0x3498db)
            )

            # Filter out non-slash commands
            commands = [cmd for cmd in plugin.all_commands 
                    if lightbulb.SlashCommand in cmd.implements]
            
            if commands:
                command_list = []
                for cmd in commands:
                    help_text = getattr(cmd, 'help_text', cmd.description)
                    command_list.append(
                        f"**{cmd.name}**\n"
                        f"└ {help_text}\n"
                        f"└ Usage: {cmd.signature}"
                    )
                
                embed.add_field(
                    name="Available Commands",
                    value="\n".join(command_list),
                    inline=False
                )
                
                embeds.append(embed)
                labels.append(plugin.name)

        if len(embeds) > 1:  # Only create view if we have plugins to show
            view = HelpView(embeds, labels, timeout=300.0)
            response = await context.respond(embed=embeds[0], components=view.build())
            message = await response.message()
            view.start(message)  # Start the view with the message
        else:
            # If no plugins found, just show the overview
            await context.respond(embed=embeds[0])

    async def send_plugin_help(self, context: lightbulb.Context, plugin: lightbulb.Plugin) -> None:
        embed = hikari.Embed(
            title=f"{plugin.name} Plugin",
            description=plugin.description or "No description provided",
            color=hikari.Color(0x3498db)
        )

        # Filter out non-slash commands
        commands = [cmd for cmd in plugin.all_commands if not isinstance(cmd, lightbulb.commands.prefix.PrefixCommand)]
        if commands:
            command_list = []
            for cmd in commands:
                # Get command help text if available
                help_text = cmd.get_help(context) if hasattr(cmd, 'get_help') else cmd.description
                
                command_list.append(
                    f"**{cmd.name}**\n"
                    f"└ {help_text}\n"
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

        await context.respond(embed=embed)

    async def send_command_help(self, context: lightbulb.Context, command: lightbulb.Command) -> None:
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

        # Add command options for slash commands
        if isinstance(command, lightbulb.SlashCommand) and command.options:
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
        if command.checks:
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

        await context.respond(embed=embed)

    async def send_group_help(self, context: lightbulb.Context, group: Union[lightbulb.SlashCommandGroup, lightbulb.PrefixCommandGroup]) -> None:
        embed = hikari.Embed(
            title=f"Command Group: {group.name}",
            description=group.description,
            color=hikari.Color(0x3498db)
        )

        for cmd in group.subcommands.values():
            help_text = cmd.get_help(context) if hasattr(cmd, 'get_help') else cmd.description
            embed.add_field(
                name=cmd.name,
                value=f"Description: {help_text}\nUsage: {cmd.signature}",
                inline=False
            )

        await context.respond(embed=embed)

    async def object_not_found(self, context: lightbulb.Context, obj: str) -> None:
        embed = hikari.Embed(
            title="Not Found",
            description=f"No command or plugin found matching '{obj}'",
            color=hikari.Color(0xff0000)
        )
        await context.respond(embed=embed)