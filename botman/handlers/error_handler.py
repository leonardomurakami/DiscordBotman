import logging
import traceback
import hikari
import lightbulb

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Handles various command and event errors."""
    
    @staticmethod
    async def handle_command_not_found(event: lightbulb.CommandErrorEvent) -> None:
        """Handle case where command doesn't exist."""
        command = str(event.exception).split("'")[1]
        embed = hikari.Embed(
            title="❌ Command Not Found",
            description=f"The command `{command}` doesn't exist!",
            color=hikari.Color(0xff0000)
        )
        embed.add_field(
            name="Need Help?",
            value="Use `!help` to see a list of all available commands.",
            inline=False
        )
        logger.error(f"User {event.context.author.username} in guild {event.context.guild_id} ran unknown command: {command}")
        await event.context.respond(embed=embed)

    @staticmethod
    async def handle_missing_permissions(event: lightbulb.CommandErrorEvent) -> None:
        """Handle case where user lacks required permissions."""
        embed = hikari.Embed(
            title="❌ Missing Permissions",
            description="You don't have the required permissions to use this command!",
            color=hikari.Color(0xff0000)
        )
        await event.context.respond(embed=embed)

    @staticmethod
    async def handle_not_owner(event: lightbulb.CommandErrorEvent) -> None:
        """Handle case where non-owner uses owner-only command."""
        embed = hikari.Embed(
            title="❌ Owner Only",
            description="This command can only be used by the bot owner!",
            color=hikari.Color(0xff0000)
        )
        await event.context.respond(embed=embed)

    @staticmethod
    async def handle_cooldown(event: lightbulb.CommandErrorEvent) -> None:
        """Handle command cooldown."""
        embed = hikari.Embed(
            title="⏳ Cooldown",
            description=f"This command is on cooldown! Try again in {event.exception.retry_after:.2f} seconds.",
            color=hikari.Color(0xff9900)
        )
        await event.context.respond(embed=embed)

    @staticmethod
    async def handle_missing_arguments(event: lightbulb.CommandErrorEvent) -> None:
        """Handle missing required arguments."""
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

    @staticmethod
    async def handle_command_invocation_error(event: lightbulb.CommandErrorEvent) -> None:
        """Handle general command execution errors."""
        embed = hikari.Embed(
            title="❌ Command Error",
            description="An error occurred while executing the command!",
            color=hikari.Color(0xff0000)
        )
        
        error_details = ''.join(traceback.format_exception(
            type(event.exception.__cause__),
            event.exception.__cause__,
            event.exception.__cause__.__traceback__
        ))
        
        logger.error(f"Command error in {event.context.command.name}: {error_details}")
        
        embed.add_field(
            name="Error Details",
            value=f"```{str(event.exception.__cause__)}```",
            inline=False
        )
        
        await event.context.respond(embed=embed)

    @staticmethod
    async def handle_unexpected_error(event: lightbulb.CommandErrorEvent) -> None:
        """Handle any unexpected errors not caught by other handlers."""
        embed = hikari.Embed(
            title="❌ Unexpected Error",
            description="An unexpected error occurred! Please try again later.",
            color=hikari.Color(0xff0000)
        )
        
        error_details = ''.join(traceback.format_exception(
            type(event.exception),
            event.exception,
            event.exception.__traceback__
        ))
        logger.error(f"Unexpected error: {error_details}")
        
        await event.context.respond(embed=embed)