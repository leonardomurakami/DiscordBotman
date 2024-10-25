import hikari
import miru
import lavalink

from typing import List, Dict

class MusicPlayerView(miru.View):
    def __init__(self, player: lavalink.DefaultPlayer) -> None:
        super().__init__(timeout=None)
        self.player = player

    @miru.button(emoji="⏮️", style=hikari.ButtonStyle.PRIMARY)
    async def previous_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        if not self.player.current:
            await ctx.respond("No track is currently playing!", flags=hikari.MessageFlag.EPHEMERAL)
            return
        
        await self.player.seek(0)
        await ctx.respond("Restarted current track!", flags=hikari.MessageFlag.EPHEMERAL)

    @miru.button(emoji="⏯️", style=hikari.ButtonStyle.PRIMARY)
    async def play_pause_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        if not self.player.current:
            await ctx.respond("No track is currently playing!", flags=hikari.MessageFlag.EPHEMERAL)
            return

        if self.player.paused:
            await self.player.set_pause(False)
            await ctx.respond("Resumed playback!", flags=hikari.MessageFlag.EPHEMERAL)
        else:
            await self.player.set_pause(True)
            await ctx.respond("Paused playback!", flags=hikari.MessageFlag.EPHEMERAL)

    @miru.button(emoji="⏭️", style=hikari.ButtonStyle.PRIMARY)
    async def skip_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        if not self.player.current:
            await ctx.respond("No track is currently playing!", flags=hikari.MessageFlag.EPHEMERAL)
            return

        await self.player.skip()
        await ctx.respond("Skipped track!", flags=hikari.MessageFlag.EPHEMERAL)

    @miru.button(emoji="🔄", style=hikari.ButtonStyle.SUCCESS)
    async def loop_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        if not self.player.current:
            await ctx.respond("No track is currently playing!", flags=hikari.MessageFlag.EPHEMERAL)
            return

        self.player.repeat = not self.player.repeat
        status = "enabled" if self.player.repeat else "disabled"
        await ctx.respond(f"Loop {status}!", flags=hikari.MessageFlag.EPHEMERAL)

    @miru.button(emoji="⏹️", style=hikari.ButtonStyle.DANGER)
    async def stop_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        if not self.player.current:
            await ctx.respond("No track is currently playing!", flags=hikari.MessageFlag.EPHEMERAL)
            return

        await self.player.stop()
        self.player.queue.clear()
        await ctx.respond("Stopped playback and cleared queue!", flags=hikari.MessageFlag.EPHEMERAL)
