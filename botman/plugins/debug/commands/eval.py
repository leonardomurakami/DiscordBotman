import asyncio
import lightbulb
import hikari

from base.command import BaseCommand


class EvalCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "eval"
        self.description = "Evaluate Python code (Owner only)"
        self.help_text = "!eval <code> or /eval <code> - Evaluates Python code (Owner only for security)"

    def create_command(self) -> lightbulb.Command:
        @self.plugin.command
        @lightbulb.add_checks(lightbulb.owner_only)
        @lightbulb.set_help(self.help_text)
        @lightbulb.option("code", "The Python code to evaluate", type=str, required=True)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd

    async def execute(self, ctx: lightbulb.Context) -> None:
        code = ctx.options.code
        try:
            globals_dict = {
                'ctx': ctx,
                'bot': ctx.bot,
                'hikari': hikari,
                'lightbulb': lightbulb
            }
            
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