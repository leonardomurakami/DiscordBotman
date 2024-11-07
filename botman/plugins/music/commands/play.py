import lightbulb
import hikari
import ongaku
import logging
import typing

from base.command import BaseCommand
from views.music_view import MusicPlayerView


class PlayCommand(BaseCommand):
    def _setup_command(self) -> None:
        self.name = "play"
        self.description = "Play a song or playlist"
        self.help_text = "!play <query> or /play <query> - Play a song or playlist"

    def create_command(self) -> lightbulb.Command:
        @self.bot.command
        @lightbulb.add_checks(lightbulb.guild_only)
        @lightbulb.option("query", "The song/playlist to play", type=str, required=True, modifier=lightbulb.OptionModifier.CONSUME_REST)
        @lightbulb.command(self.name, self.description)
        @lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
        async def cmd(ctx: lightbulb.Context) -> None:
            await self.execute(ctx)
        return cmd

    async def execute(self, ctx: lightbulb.Context) -> None:
        SOURCE_PREFIXES = {
            "spotify:": "spsearch:",
            "sc:": "scsearch:",
            "soundcloud:": "scsearch:",
            "yt:": "ytsearch:",
            "youtube:": "ytsearch:",
        }

        voice_state = ctx.bot.cache.get_voice_state(ctx.guild_id, ctx.author.id)
        if not voice_state or not voice_state.channel_id:
            await ctx.respond("You must be in a voice channel to use this command!")
            return

        try:
            player = ctx.bot.d.ongaku.create_player(ctx.get_guild())
            
            if not player.connected:
                await player.connect(voice_state.channel_id, deaf=True)

            loading_msg = await ctx.respond("🔍 Searching...", flags=hikari.MessageFlag.EPHEMERAL)

            query = ctx.options.query
            is_direct_url = any(s in query.lower() for s in ['http://', 'https://', 'www.'])

            if not is_direct_url:
                used_prefix = next((prefix for prefix in SOURCE_PREFIXES if query.lower().startswith(prefix)), None)
                if used_prefix:
                    query = SOURCE_PREFIXES[used_prefix] + query[len(used_prefix):].strip()
                else:
                    query = f"ytsearch:{query}"

            result = await ctx.bot.d.ongaku.rest.load_track(query)
            
            if result is None:
                await loading_msg.edit("❌ No results found!")
                return

            was_playing = bool(player.queue)

            if isinstance(result, typing.Sequence):
                if not is_direct_url:
                    tracks = [result[0]]
                else:
                    tracks = result
                
                first_track = tracks[0]
                player.add(tracks)
                
                embed = hikari.Embed(
                    title="Playlist Added" if len(tracks) > 1 else "Track Added",
                    description=f"Added {len(tracks)} tracks to the queue" if len(tracks) > 1 else f"Added track to the queue",
                    color=hikari.Color(0x3498db)
                )
                
                track_list = "\n".join(
                    f"`{i+1}.` {track.info.title}"
                    for i, track in enumerate(tracks[:5])
                )
                if len(tracks) > 5:
                    track_list += f"\n... and {len(tracks) - 5} more"
                
                embed.add_field(
                    name="Tracks" if len(tracks) > 1 else "Track",
                    value=track_list,
                    inline=False
                )
                
                total_duration = sum(track.info.length for track in tracks)
                minutes, seconds = divmod(total_duration // 1000, 60)
                hours, minutes = divmod(minutes, 60)
                
                duration_str = f"{hours}:{minutes:02d}:{seconds:02d}" if hours > 0 else f"{minutes}:{seconds:02d}"
                    
                embed.add_field(
                    name="Total Duration",
                    value=duration_str,
                    inline=True
                )
                
                await loading_msg.edit(embed=embed)
                
                if not was_playing:
                    await player.play()
                    await self.update_music_view(ctx, player, first_track)
                    
            else:
                track = result
                player.add(track)
                
                duration = track.info.length // 1000
                minutes, seconds = divmod(duration, 60)
                
                embed = hikari.Embed(
                    title="Track Enqueued",
                    description=f"🎵 {track.info.title}",
                    color=hikari.Color(0x3498db)
                )
                
                embed.add_field(
                    name="Duration",
                    value=f"{minutes}:{seconds:02d}",
                    inline=True
                )
                if track.info.author:
                    embed.add_field(
                        name="Artist",
                        value=track.info.author,
                        inline=True
                    )
                
                if was_playing:
                    position = len(player.queue)
                    embed.add_field(
                        name="Position",
                        value=f"#{position} in queue",
                        inline=True
                    )
                
                await loading_msg.edit(embed=embed)
                
                if not was_playing:
                    await player.play()
                    await self.update_music_view(ctx, player, track)

        except Exception as e:
            logging.error(f"Error in play command: {e}", exc_info=True)
            await ctx.respond(f"An error occurred: {str(e)}")

    async def update_music_view(self, ctx: lightbulb.Context, player: ongaku.Player, track: ongaku.Track) -> None:
        view = MusicPlayerView(player)
        embed = self.create_now_playing_embed(track)
        
        try:
            if ctx.guild_id in ctx.bot.d.active_views:
                old_view = ctx.bot.d.active_views[ctx.guild_id]
                
                new_message = await ctx.respond(
                    embed=embed,
                    components=view.build(),
                )
                
                view.message = new_message
                ctx.bot.d.active_views[ctx.guild_id] = view
                ctx.bot.d.miru.start_view(view)
                
                try:
                    await old_view.message.delete()
                except Exception as e:
                    logging.error(f"Failed to delete old music player message: {e}")
            else:
                new_message = await ctx.respond(
                    embed=embed,
                    components=view.build(),
                )
                
                view.message = new_message
                ctx.bot.d.active_views[ctx.guild_id] = view
                ctx.bot.d.miru.start_view(view)
                
        except Exception as e:
            logging.error(f"Failed to update music view: {e}")
            await ctx.respond(f"An error occurred: {str(e)}")

    def create_now_playing_embed(self, track: ongaku.Track) -> hikari.Embed:
        duration = track.info.length // 1000
        minutes, seconds = divmod(duration, 60)
        
        embed = hikari.Embed(
            title="Music Player",
            color=hikari.Color(0x3498db)
        )
        
        embed.add_field(
            name="Now Playing",
            value=f"🎵 {track.info.title}",
            inline=False
        )
        
        embed.add_field(
            name="Duration",
            value=f"{minutes:02d}:{seconds:02d}",
            inline=True
        )
        
        if track.info.author:
            embed.add_field(
                name="Artist",
                value=track.info.author,
                inline=True
            )

        if track.info.artwork_url:
            embed.set_thumbnail(track.info.artwork_url)
        
        embed.set_footer(text="Use the controls below to control playback")
        return embed