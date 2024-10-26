import hikari
import ongaku
import lightbulb
import logging
import typing
import asyncio
from datetime import datetime
from views.music_view import MusicPlayerView

plugin = lightbulb.Plugin("music")
plugin.description = "Music commands for playing audio in voice channels"
logger = logging.getLogger(__name__)

# Global variables
active_views = {}
voice_timeouts = {}  # Store timeout tasks for each guild
TIMEOUT_SECONDS = 300  # 5 minutes timeout when alone in channel

async def cleanup_player(guild_id: int, bot: lightbulb.BotApp) -> None:
    """Helper function to clean up player resources"""
    try:
        # Clear the view if it exists
        if guild_id in active_views:
            view = active_views[guild_id]
            try:
                await view.message.delete()
            except Exception as e:
                logger.error(f"Failed to delete music player message during cleanup: {e}")
            del active_views[guild_id]

        # Cancel any existing timeout task
        if guild_id in voice_timeouts:
            voice_timeouts[guild_id].cancel()
            del voice_timeouts[guild_id]

        # Clean up player
        player = bot.d.ongaku.create_player(guild_id)
        if player:
            await player.stop()
            await player.disconnect()
            bot.d.ongaku.delete_player(guild_id)

    except Exception as e:
        logger.error(f"Error during player cleanup: {e}")

async def start_timeout_task(guild_id: int, bot: lightbulb.BotApp) -> None:
    """Start a timeout task for a guild"""
    try:
        # Cancel any existing timeout task
        if guild_id in voice_timeouts:
            voice_timeouts[guild_id].cancel()
        
        # Create new timeout task
        task = asyncio.create_task(handle_timeout(guild_id, bot))
        voice_timeouts[guild_id] = task
    except Exception as e:
        logger.error(f"Error starting timeout task: {e}")

async def handle_timeout(guild_id: int, bot: lightbulb.BotApp) -> None:
    """Handle timeout when bot is alone in channel"""
    try:
        await asyncio.sleep(TIMEOUT_SECONDS)
        player = bot.d.ongaku.create_player(guild_id)
        
        if player and player.connected:
            # Double check if still alone before disconnecting
            voice_states = bot.cache.get_voice_states_view_for_channel(
                guild_id,
                player.channel_id
            )
            if len([vs for vs in voice_states.values() if not vs.member.is_bot]) == 0:
                await cleanup_player(guild_id, bot)
                logger.info(f"Disconnected from voice in guild {guild_id} due to timeout")
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Error in timeout handler: {e}")
    finally:
        if guild_id in voice_timeouts:
            del voice_timeouts[guild_id]

def create_now_playing_embed(track: ongaku.Track) -> hikari.Embed:
    """Create a standardized now playing embed with track art"""
    duration = track.info.length // 1000
    minutes, seconds = divmod(duration, 60)
    
    embed = hikari.Embed(
        title="Music Player",
        color=hikari.Color(0x3498db)
    )
    
    # Main track info
    embed.add_field(
        name="Now Playing",
        value=f"🎵 {track.info.title}",
        inline=False
    )
    
    # Add duration and artist in the same row
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

    # Add track thumbnail if available
    if track.info.artwork_url:
        embed.set_thumbnail(track.info.artwork_url)
    
    embed.set_footer(text="Use the controls below to control playback")
    return embed

async def update_music_view(ctx: lightbulb.Context, player: ongaku.Player, track: ongaku.Track) -> None:
    """Helper function to update or create a new music view"""
    view = MusicPlayerView(player)
    embed = create_now_playing_embed(track)
    
    try:
        if ctx.guild_id in active_views:
            old_view = active_views[ctx.guild_id]
            
            new_message = await ctx.respond(
                embed=embed,
                components=view.build(),
            )
            
            view.message = new_message
            active_views[ctx.guild_id] = view
            ctx.bot.d.miru.start_view(view)
            
            try:
                await old_view.message.delete()
            except Exception as e:
                logger.error(f"Failed to delete old music player message: {e}")
        else:
            new_message = await ctx.respond(
                embed=embed,
                components=view.build(),
            )
            
            view.message = new_message
            active_views[ctx.guild_id] = view
            ctx.bot.d.miru.start_view(view)
            
    except Exception as e:
        logger.error(f"Failed to update music view: {e}")
        await ctx.respond(f"An error occurred: {str(e)}")

@plugin.listener(ongaku.TrackStartEvent)
async def on_track_start(event: ongaku.TrackStartEvent) -> None:
    """Handle track start events to update the music view"""
    guild_id = event.guild_id
    if guild_id in active_views:
        try:
            old_view = active_views[guild_id]
            channel_id = old_view.message.channel_id
            del(active_views[guild_id])
            try:
                await old_view.message.delete()
            except Exception as e:
                logger.error(f"Failed to delete old music player message: {e}")
            
            channel = await event.client.app.rest.fetch_channel(channel_id)
            if channel:
                player = event.client.fetch_player(guild_id)
                view = MusicPlayerView(player)
                
                embed = create_now_playing_embed(event.track)
                message = await channel.send(
                    embed=embed,
                    components=view.build()
                )
                view.message = message
                
                event.client.app.d.miru.start_view(view)
                active_views[guild_id] = view

        except Exception as e:
            logger.error(f"Failed to update view on track start: {e}")

@plugin.listener(ongaku.TrackEndEvent)
async def on_track_end(event: ongaku.TrackEndEvent) -> None:
    """Handle track end events"""
    player = event.client.fetch_player(event.guild_id)
    
    if not player.queue:
        if player.autoplay:
            # If queue is empty and autoplay is on, try to load a related track
            try:
                result = await player.client.d.ongaku.rest.load_track(
                    f"ytsearch:{event.track.info.title} similar"
                )
                if isinstance(result, typing.Sequence) and result:
                    player.add(result[0])
                    await player.play()
                else:
                    # No related tracks found, clean up
                    await cleanup_player(event.guild_id, event.client.app)
            except Exception as e:
                logger.error(f"Failed to load autoplay track: {e}")
                await cleanup_player(event.guild_id, event.client.app)
        else:
            # Queue is empty and autoplay is off, clean up
            await cleanup_player(event.guild_id, event.client.app)

@plugin.listener(hikari.VoiceStateUpdateEvent)
async def on_voice_state_update(event: hikari.VoiceStateUpdateEvent) -> None:
    """Handle disconnects and empty voice channels"""
    if not event.guild_id:
        return
        
    player = plugin.bot.d.ongaku.create_player(event.guild_id)
    if not player.connected:
        return
        
    # Get the voice states for the channel the bot is in
    voice_states = plugin.bot.cache.get_voice_states_view_for_channel(
        event.guild_id,
        player.channel_id
    )
    
    # Check if the bot is alone in the channel
    if len([vs for vs in voice_states.values() if not vs.member.is_bot]) == 0:
        # Start timeout task instead of disconnecting immediately
        await start_timeout_task(event.guild_id, plugin.bot)
    else:
        # Cancel timeout task if not alone
        if event.guild_id in voice_timeouts:
            voice_timeouts[event.guild_id].cancel()
            del voice_timeouts[event.guild_id]

@plugin.command
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("join", "Join your voice channel")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def join(ctx: lightbulb.Context) -> None:
    states = ctx.bot.cache.get_voice_states_view_for_guild(ctx.guild_id)
    voice_state = [state for state in states.values() if state.user_id == ctx.author.id]
    
    if not voice_state:
        await ctx.respond("You're not in a voice channel!")
        return
        
    channel_id = voice_state[0].channel_id
    try:
        player = ctx.bot.d.ongaku.create_player(ctx.guild_id)
        await player.connect(channel_id, deaf=True)
        await ctx.respond(f"Joined <#{channel_id}>!")
    except Exception as e:
        logger.error(f"Failed to join voice channel: {e}")
        await ctx.respond(f"Failed to join voice channel: {str(e)}")

@plugin.command()
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.option("query", "The song/playlist to play", type=str, required=True, modifier=lightbulb.OptionModifier.CONSUME_REST)
@lightbulb.command("play", "Play a song or playlist")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def play(ctx: lightbulb.Context) -> None:
    # Source prefixes mapping to Lavalink search prefixes
    SOURCE_PREFIXES = {
        "spotify:": "spsearch:",  # Spotify search
        "sc:": "scsearch:",       # SoundCloud search
        "soundcloud:": "scsearch:",# SoundCloud search alternative
        "yt:": "ytsearch:",       # YouTube search
        "youtube:": "ytsearch:",  # YouTube search alternative
    }

    voice_state = ctx.bot.cache.get_voice_state(ctx.guild_id, ctx.author.id)
    if not voice_state or not voice_state.channel_id:
        await ctx.respond("You must be in a voice channel to use this command!")
        return

    try:
        player = ctx.bot.d.ongaku.create_player(ctx.get_guild())
        
        if not player.connected:
            await player.connect(voice_state.channel_id, deaf=True)

        # Send initial loading message for better UX
        loading_msg = await ctx.respond("🔍 Searching...", flags=hikari.MessageFlag.EPHEMERAL)

        query = ctx.options.query
        is_direct_url = any(s in query.lower() for s in ['http://', 'https://', 'www.'])

        # Handle source prefixes if not a direct URL
        if not is_direct_url:
            # Check for source prefixes
            used_prefix = next((prefix for prefix in SOURCE_PREFIXES if query.lower().startswith(prefix)), None)
            if used_prefix:
                # Remove the source prefix from query and add appropriate Lavalink prefix
                query = SOURCE_PREFIXES[used_prefix] + query[len(used_prefix):].strip()
            else:
                # Default to YouTube search if no prefix specified
                query = f"ytsearch:{query}"

        result = await ctx.bot.d.ongaku.rest.load_track(query)
        
        if result is None:
            await loading_msg.edit("❌ No results found!")
            return

        was_playing = bool(player.queue)

        if isinstance(result, typing.Sequence):
            # Multiple tracks - only allow if it's a direct URL
            if not is_direct_url:
                # If it's a search result, only take the first track
                tracks = [result[0]]
            else:
                # It's a playlist URL, keep all tracks
                tracks = result
            
            first_track = tracks[0]
            player.add(tracks)
            
            # Create embed
            embed = hikari.Embed(
                title="Playlist Added" if len(tracks) > 1 else "Track Added",
                description=f"Added {len(tracks)} tracks to the queue" if len(tracks) > 1 else f"Added track to the queue",
                color=hikari.Color(0x3498db)
            )
            
            # Add track names
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
            
            # Add total duration
            total_duration = sum(track.info.length for track in tracks)
            minutes, seconds = divmod(total_duration // 1000, 60)
            hours, minutes = divmod(minutes, 60)
            
            if hours > 0:
                duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                duration_str = f"{minutes}:{seconds:02d}"
                
            embed.add_field(
                name="Total Duration",
                value=duration_str,
                inline=True
            )
            
            await loading_msg.edit(embed=embed)
            
            if not was_playing:
                await player.play()
                await update_music_view(ctx, player, first_track)
                
        else:
            # Single track
            track = result
            player.add(track)
            
            # Create embed for single track
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
                await update_music_view(ctx, player, track)

    except Exception as e:
        logger.error(f"Error in play command: {e}", exc_info=True)
        await ctx.respond(f"An error occurred: {str(e)}")
        
@plugin.command
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("pause", "Pause or resume playback")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def pause(ctx: lightbulb.Context) -> None:
    player = ctx.bot.d.ongaku.create_player(ctx.guild_id)
    
    if not player.connected or not player.queue:
        await ctx.respond("Nothing is playing!")
        return
        
    await player.pause()
    status = "paused" if player.is_paused else "resumed"
    await ctx.respond(f"Playback {status}!")

@plugin.command
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("skip", "Skip the current track")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def skip(ctx: lightbulb.Context) -> None:
    player = ctx.bot.d.ongaku.create_player(ctx.guild_id)
    
    if not player.connected or not player.queue:
        await ctx.respond("Nothing is playing!")
        return
        
    await player.skip()
    await ctx.respond("Skipped the current track!")

@plugin.command
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.option("volume", "Volume level (0-150)", type=int, min_value=0, max_value=150, required=True)
@lightbulb.command("volume", "Set the playback volume")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def volume(ctx: lightbulb.Context) -> None:
    player = ctx.bot.d.ongaku.create_player(ctx.guild_id)
    
    if not player.connected:
        await ctx.respond("Not connected to a voice channel!")
        return
        
    await player.set_volume(ctx.options.volume)
    await ctx.respond(f"Volume set to {ctx.options.volume}%")

@plugin.command
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("shuffle", "Shuffle the queue")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def shuffle(ctx: lightbulb.Context) -> None:
    player = ctx.bot.d.ongaku.create_player(ctx.guild_id)
    
    if not player.connected or len(player.queue) < 2:
        await ctx.respond("Not enough tracks in the queue to shuffle!")
        return
        
    player.shuffle()
    await ctx.respond("Queue shuffled!")

@plugin.command
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.option("position", "Queue position to remove", type=int, required=True)
@lightbulb.command("remove", "Remove a track from the queue")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def remove(ctx: lightbulb.Context) -> None:
    player = ctx.bot.d.ongaku.create_player(ctx.guild_id)
    
    if not player.connected or not player.queue:
        await ctx.respond("Queue is empty!")
        return
        
    try:
        position = ctx.options.position - 1  # Convert to 0-based index
        if 0 <= position < len(player.queue):
            removed_track = player.queue[position]
            player.remove(position)
            await ctx.respond(f"Removed: {removed_track.info.title}")
        else:
            await ctx.respond("Invalid queue position!")
    except Exception as e:
        await ctx.respond(f"Failed to remove track: {str(e)}")

@plugin.command
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("clear", "Clear the queue")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def clear(ctx: lightbulb.Context) -> None:
    player = ctx.bot.d.ongaku.create_player(ctx.guild_id)
    
    if not player.connected:
        await ctx.respond("Not connected to a voice channel!")
        return
        
    await player.clear()
    await ctx.respond("Queue cleared!")

@plugin.command
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("nowplaying", "Show information about the current track")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def nowplaying(ctx: lightbulb.Context) -> None:
    player = ctx.bot.d.ongaku.create_player(ctx.guild_id)
    
    if not player.connected or not player.queue:
        await ctx.respond("Nothing is playing!")
        return
        
    current_track = player.queue[0]
    embed = create_now_playing_embed(current_track)
    await ctx.respond(embed=embed)

@plugin.command
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.option("state", "Enable or disable looping", type=bool, required=False)
@lightbulb.command("loop", "Toggle track looping")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def loop(ctx: lightbulb.Context) -> None:
    player = ctx.bot.d.ongaku.create_player(ctx.guild_id)
    
    if not player.connected:
        await ctx.respond("Not connected to a voice channel!")
        return
        
    state = ctx.options.state if ctx.options.state is not None else None
    new_state = player.set_loop(state)
    status = "enabled" if new_state else "disabled"
    await ctx.respond(f"Loop {status}!")

@plugin.command
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.option("state", "Enable or disable autoplay", type=bool, required=False)
@lightbulb.command("autoplay", "Toggle autoplay")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def autoplay(ctx: lightbulb.Context) -> None:
    player = ctx.bot.d.ongaku.create_player(ctx.guild_id)
    
    if not player.connected:
        await ctx.respond("Not connected to a voice channel!")
        return
        
    state = ctx.options.state if ctx.options.state is not None else None
    new_state = player.set_autoplay(state)
    status = "enabled" if new_state else "disabled"
    await ctx.respond(f"Autoplay {status}!")

@plugin.command
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("stop", "Stop playing and clear the queue")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def stop(ctx: lightbulb.Context) -> None:
    player = ctx.bot.d.ongaku.create_player(ctx.guild_id)
    
    if not player.connected:
        await ctx.respond("Not connected to a voice channel!")
        return
        
    await cleanup_player(ctx.guild_id, ctx.bot)
    await ctx.respond("Stopped playback and cleared queue!")

@plugin.command
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("leave", "Leave the voice channel")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def leave(ctx: lightbulb.Context) -> None:
    player = ctx.bot.d.ongaku.create_player(ctx.guild_id)
    
    if not player.connected:
        await ctx.respond("Not connected to a voice channel!")
        return
        
    await cleanup_player(ctx.guild_id, ctx.bot)
    await ctx.respond("Left the voice channel!")

@plugin.command
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("queue", "Show the current queue")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def queue(ctx: lightbulb.Context) -> None:
    player = ctx.bot.d.ongaku.create_player(ctx.guild_id)
    
    if not player.connected:
        await ctx.respond("Not connected to a voice channel!")
        return
        
    if not player.queue:
        await ctx.respond("The queue is empty!")
        return
        
    embed = hikari.Embed(
        title="Music Queue",
        color=hikari.Color(0x3498db)
    )
    
    # Current track
    current_track = player.queue[0]
    duration = current_track.info.length // 1000
    minutes, seconds = divmod(duration, 60)
    
    embed.add_field(
        name="Now Playing",
        value=f"🎵 {current_track.info.title}\n`{minutes:02d}:{seconds:02d}` - {current_track.info.author}",
        inline=False
    )
    
    # Upcoming tracks
    if len(player.queue) > 1:
        upcoming = []
        total_duration = 0
        
        for idx, track in enumerate(player.queue[1:], 1):
            if idx <= 10:  # Show only first 10 tracks
                duration = track.info.length // 1000
                minutes, seconds = divmod(duration, 60)
                upcoming.append(f"`{idx}.` {track.info.title} `({minutes:02d}:{seconds:02d})`")
            total_duration += track.info.length // 1000
        
        queue_text = "\n".join(upcoming)
        
        if len(player.queue) > 11:
            queue_text += f"\n\n*...and {len(player.queue) - 11} more tracks*"
        
        # Calculate total duration
        hours, remainder = divmod(total_duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            duration_text = f"{hours}h {minutes}m {seconds}s"
        else:
            duration_text = f"{minutes}m {seconds}s"
            
        embed.add_field(
            name=f"Up Next ({len(player.queue) - 1} tracks)",
            value=queue_text,
            inline=False
        )
        
        embed.add_field(
            name="Queue Duration",
            value=duration_text,
            inline=True
        )
    
    # Add player status
    status_text = []
    if player.loop:
        status_text.append("🔁 Loop enabled")
    if player.autoplay:
        status_text.append("♾️ Autoplay enabled")
    if player.is_paused:
        status_text.append("⏸️ Paused")
    
    if status_text:
        embed.add_field(
            name="Status",
            value=" | ".join(status_text),
            inline=True
        )
    
    await ctx.respond(embed=embed)

@plugin.command
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.option("seconds", "Number of seconds to seek", type=int, required=True)
@lightbulb.command("seek", "Seek to a position in the current track")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def seek(ctx: lightbulb.Context) -> None:
    player = ctx.bot.d.ongaku.create_player(ctx.guild_id)
    
    if not player.connected or not player.queue:
        await ctx.respond("Nothing is playing!")
        return
    
    try:
        position = ctx.options.seconds * 1000  # Convert to milliseconds
        current_track = player.queue[0]
        
        if position < 0 or position > current_track.info.length:
            await ctx.respond("Invalid position! Must be within track duration.")
            return
            
        await player.set_position(position)
        minutes, seconds = divmod(position // 1000, 60)
        await ctx.respond(f"Seeked to position: {minutes:02d}:{seconds:02d}")
    except Exception as e:
        await ctx.respond(f"Failed to seek: {str(e)}")

def load(bot: lightbulb.BotApp) -> None:
    global active_views, voice_timeouts
    active_views = {}
    voice_timeouts = {}
    bot.add_plugin(plugin)

def unload(bot: lightbulb.BotApp) -> None:
    # Clean up all active players when plugin unloads
    for guild_id in list(active_views.keys()):
        asyncio.create_task(cleanup_player(guild_id, bot))
    bot.remove_plugin(plugin)