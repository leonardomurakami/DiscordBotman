import lightbulb
import hikari

from base.command import BaseCommand

class PrefixCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "prefix"
        self.description = "View or set the server prefix"
        self.help_text = "!prefix [new_prefix] or /prefix [new_prefix] - View or change the server prefix"

    def create_command(self) -> lightbulb.Command:
        @self.plugin.command
        @lightbulb.set_help(self.help_text)
        @lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_GUILD))
        @lightbulb.option("new_prefix", "The new prefix to set", type=str, required=False)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd

    async def execute(self, ctx: lightbulb.Context) -> None:
        if ctx.options.new_prefix:
            if len(ctx.options.new_prefix) > 5:
                await ctx.respond("Prefix must be 5 characters or less!")
                return

            success = await ctx.bot.d.api_client.set_guild_prefix(
                str(ctx.guild_id),
                ctx.options.new_prefix
            )

            if success:
                embed = hikari.Embed(
                    title="Prefix Updated",
                    description=f"Server prefix has been set to: `{ctx.options.new_prefix}`",
                    color=hikari.Color(0x00ff00)
                )
            else:
                embed = hikari.Embed(
                    title="Error",
                    description="Failed to update prefix. Please try again later.",
                    color=hikari.Color(0xff0000)
                )
        else:
            current_prefix = await ctx.bot.d.api_client.get_guild_prefix(str(ctx.guild_id))
            embed = hikari.Embed(
                title="Current Prefix",
                description=f"The current server prefix is: `{current_prefix}`",
                color=hikari.Color(0x00ff00)
            )
        
        await ctx.respond(embed=embed)