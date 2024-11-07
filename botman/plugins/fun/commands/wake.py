import lightbulb
import hikari
import random
import asyncio

from base.command import BaseCommand


class WakeCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "wake"
        self.description = "Wake up a user in voice chat"
        self.help_text = "!wake <user> or /wake <user> - Moves a user between voice channels briefly to get their attention"

    def create_command(self) -> lightbulb.Command:
        @self.plugin.command
        @lightbulb.set_help(self.help_text)
        @lightbulb.option("times", "Number of moves (default: 5, max: 10)", type=int, required=False, default=5)
        @lightbulb.option("user", "The user to wake up", type=hikari.Member, required=True)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd

    async def execute(self, ctx: lightbulb.Context) -> None:
        target_user = ctx.options.user
        target_user_voicestate = ctx.bot.cache.get_voice_state(ctx.guild_id, target_user.id)
        times = min(max(1, ctx.options.times), 10)
        
        if not target_user_voicestate:
            embed = hikari.Embed(
                title="Error",
                description=f"{target_user.mention} is not in a voice channel!",
                color=hikari.Color(0xff0000)
            )
            await ctx.respond(embed=embed)
            return

        original_channel = target_user_voicestate.channel_id
        guild = ctx.get_guild()
        available_channels = []
        
        for channel in guild.get_channels().values():
            if isinstance(channel, hikari.GuildVoiceChannel):
                member_count = len(ctx.bot.cache.get_voice_states_view_for_channel(
                    ctx.guild_id,
                    channel.id
                ))
                
                if member_count == 0 or (member_count == 1 and target_user_voicestate.channel_id == channel.id):
                    permissions = lightbulb.utils.permissions_in(channel, target_user)
                    if permissions & hikari.Permissions.CONNECT:
                        available_channels.append(channel.id)
        
        if len(available_channels) < 2:
            embed = hikari.Embed(
                title="Error",
                description="Not enough available voice channels to perform the wake command!",
                color=hikari.Color(0xff0000)
            )
            await ctx.respond(embed=embed)
            return
        
        embed = hikari.Embed(
            title="Wake Command",
            description=f"Waking up {target_user.mention}...",
            color=hikari.Color(0x3498db)
        )
        await ctx.respond(embed=embed)
        
        try:
            for i in range(times):
                current_channel = target_user_voicestate.channel_id
                temp_channels = [c for c in available_channels if c != current_channel]
                
                if not temp_channels:
                    break
                    
                next_channel = random.choice(temp_channels)
                await target_user.edit(voice_channel=next_channel)
                await asyncio.sleep(0.5)
            
            await target_user.edit(voice_channel=original_channel)
                
            embed = hikari.Embed(
                title="Wake Command",
                description=f"Successfully woke up {target_user.mention}!",
                color=hikari.Color(0x00ff00)
            )
            await ctx.edit_last_response(embed=embed)
                
        except hikari.ForbiddenError:
            embed = hikari.Embed(
                title="Error",
                description="I don't have permission to move that user!",
                color=hikari.Color(0xff0000)
            )
            await ctx.edit_last_response(embed=embed)
        except Exception as e:
            embed = hikari.Embed(
                title="Error",
                description=f"An error occurred: {str(e)}",
                color=hikari.Color(0xff0000)
            )
            await ctx.edit_last_response(embed=embed)