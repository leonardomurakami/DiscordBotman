import hikari
import miru
import ongaku
import typing

from typing import Literal

class MusicPlayerView(miru.View):
    def __init__(self, player: ongaku.Player) -> None:
        super().__init__(timeout=None)
        self.player = player
        # Initialize play/pause button with play state
        self._update_play_pause_button()
        
    @property
    def message(self) -> typing.Optional[hikari.Message]:
        return self._message

    @message.setter
    def message(self, value: hikari.Message) -> None:
        self._message = value

    def _update_play_pause_button(self) -> None:
        """Updates the play/pause button style and emoji based on player state"""
        button = self.play_pause_button
        if not self.player.is_paused:
            button.emoji = "▶️"  # Play emoji
            button.style = hikari.ButtonStyle.SUCCESS  # Green when ready to play
        else:
            button.emoji = "⏸️"  # Pause emoji
            button.style = hikari.ButtonStyle.DANGER  # Red when ready to pause

    @miru.button(emoji="⏮️", style=hikari.ButtonStyle.SECONDARY, row=0)
    async def restart_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        if not self.player.queue:
            await ctx.respond("No track is currently playing!", flags=hikari.MessageFlag.EPHEMERAL)
            return
        
        await self.player.set_position(0)
        await ctx.respond("Restarted current track!", flags=hikari.MessageFlag.EPHEMERAL)

    @miru.button(emoji="▶️", style=hikari.ButtonStyle.SUCCESS, row=0)
    async def play_pause_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        if not self.player.queue:
            await ctx.respond("No track is currently playing!", flags=hikari.MessageFlag.EPHEMERAL)
            return

        await self.player.pause()  # Toggle pause state
        self._update_play_pause_button()
        
        status = "Resumed" if not self.player.is_paused else "Paused"
        await ctx.edit_response(components=self)  # Update button appearance

    @miru.button(emoji="⏭️", style=hikari.ButtonStyle.SECONDARY, row=0)
    async def skip_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        if not self.player.queue:
            await ctx.respond("No track is currently playing!", flags=hikari.MessageFlag.EPHEMERAL)
            return

        await self.player.skip()
        await ctx.respond("Skipped track!", flags=hikari.MessageFlag.EPHEMERAL)

    @miru.button(emoji="🔁", style=hikari.ButtonStyle.SECONDARY, row=1)
    async def loop_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        if not self.player.queue:
            await ctx.respond("No track is currently playing!", flags=hikari.MessageFlag.EPHEMERAL)
            return

        new_state = self.player.set_loop()  # Toggles loop state
        button.style = hikari.ButtonStyle.SUCCESS if new_state else hikari.ButtonStyle.SECONDARY
        status = "enabled" if new_state else "disabled"
        await ctx.edit_response(components=self)  # Update button appearance

    @miru.button(emoji="♾️", style=hikari.ButtonStyle.SECONDARY, row=1)
    async def autoplay_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        if not self.player.queue:
            await ctx.respond("No track is currently playing!", flags=hikari.MessageFlag.EPHEMERAL)
            return

        new_state = self.player.set_autoplay()
        button.style = hikari.ButtonStyle.SUCCESS if new_state else hikari.ButtonStyle.SECONDARY
        await ctx.edit_response(components=self)

    @miru.button(emoji="⏹️", style=hikari.ButtonStyle.SECONDARY, row=1)
    async def stop_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        if not self.player.queue:
            await ctx.respond("No track is currently playing!", flags=hikari.MessageFlag.EPHEMERAL)
            return

        await self.player.stop()
        # Reset play/pause button to play state
        self.play_pause_button.emoji = "▶️"
        self.play_pause_button.style = hikari.ButtonStyle.SUCCESS
        await ctx.edit_response(components=self)  # Update button appearance