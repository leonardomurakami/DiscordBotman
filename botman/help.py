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

        # Create an embed for each plugin
        for plugin in context.bot.plugins.values():
            if not plugin.all_commands:
                continue

            embed = hikari.Embed(
                title=f"{plugin.name} Plugin",
                description=plugin.description or "No description provided",
                color=hikari.Color(0x3498db)
            )


            commands = [cmd for cmd in plugin.all_commands if not isinstance(cmd, lightbulb.commands.prefix.PrefixCommand)]
            command_list = []
            for cmd in commands:
                command_list.append(
                    f"**{cmd.name}**\n"
                    f"└ {cmd.description}\n"
                    f"└ Usage: {cmd.signature}"
                )
            embed.add_field(
                name=f"Available commands!",
                value="\n".join(command_list),
                inline=False
            )

            embeds.append(embed)
            labels.append(plugin.name)

        # Send embeds with navigation
        view = HelpView(embeds, labels, timeout=300.0)
        response = await context.respond(embed=embeds[0], components=view.build())
        message = await response.message()
        context.app.d.miru.start_view(view)

    async def send_plugin_help(self, context: lightbulb.Context, plugin: lightbulb.Plugin) -> None:
        if not plugin.all_commands:
            await context.respond(
                hikari.Embed(
                    title="No commands",
                    description="This plugin doesn't have any commands",
                    color=hikari.Color(0xff0000)
                )
            )

        embed = hikari.Embed(
            title=f"{plugin.name} Plugin",
            description=plugin.description or "No description provided",
            color=hikari.Color(0x3498db)
        )


        commands = [cmd for cmd in plugin.all_commands if not isinstance(cmd, lightbulb.commands.prefix.PrefixCommand)]
        command_list = []
        for cmd in commands:
            command_list.append(
                f"**{cmd.name}**\n"
                f"└ {cmd.description}\n"
                f"└ Usage: {cmd.signature}"
            )
        embed.add_field(
            name=f"Available commands!",
            value="\n".join(command_list),
            inline=False
        )

        await context.respond(embed=embed)

    async def send_command_help(self, context: lightbulb.Context, command: lightbulb.Command) -> None:
        embed = hikari.Embed(
            title=f"Command: {command.name}",
            description=command.description,
            color=hikari.Color(0x3498db)
        )

        # Add basic command info
        embed.add_field(
            name="Usage",
            value=command.signature,
            inline=False
        )

        # Add implementation types
        if hasattr(command, "implements"):
            impl_types = [impl.__name__ for impl in command.implements]
            embed.add_field(
                name="Command Type",
                value=", ".join(impl_types),
                inline=False
            )

        # Add options if it's a slash command
        if lightbulb.SlashCommand in getattr(command, "implements", []):
            if command.options:
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

        await context.respond(embed=embed)

    async def send_group_help(self, context: lightbulb.Context, group: Union[lightbulb.SlashCommandGroup, lightbulb.PrefixCommandGroup]) -> None:
        embed = hikari.Embed(
            title=f"Command Group: {group.name}",
            description=group.description,
            color=hikari.Color(0x3498db)
        )

        for cmd in group.subcommands.values():  # This one stays as .values() since it's a different structure
            embed.add_field(
                name=cmd.name,
                value=f"Description: {cmd.description}\nUsage: {getattr(cmd, 'usage', 'No usage specified')}",
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