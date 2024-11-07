import lightbulb
import hikari
import random
import string

from base.command import BaseCommand


class PasswordCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "password"
        self.description = "Generate a secure random password"
        self.help_text = "!password <length> or /password - Generate a secure random password"

    def create_command(self) -> lightbulb.Command:
        @self.plugin.command
        @lightbulb.set_help(self.help_text)
        @lightbulb.option("length", "Password length", type=int, required=False, default=16)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd

    async def execute(self, ctx: lightbulb.Context) -> None:
        length = max(8, min(ctx.options.length, 32))
        
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        special = "!@#$%^&*"
        
        password = [
            random.choice(lowercase),
            random.choice(uppercase),
            random.choice(digits),
            random.choice(special)
        ]
        
        all_chars = lowercase + uppercase + digits + special
        password.extend(random.choice(all_chars) for _ in range(length - 4))
        
        random.shuffle(password)
        password_str = "".join(password)
        
        embed = hikari.Embed(
            title="🔒 Password Generated",
            description=f"||`{password_str}`||",
            color=hikari.Color(0x1abc9c)
        )
        embed.add_field("Length", str(length), inline=True)
        embed.set_footer(text="This message will be automatically deleted in 1 minute.\nThis bot will never store the generated passwords.")
        
        await ctx.respond(embed=embed, flags=hikari.MessageFlag.EPHEMERAL, delete_after=60)