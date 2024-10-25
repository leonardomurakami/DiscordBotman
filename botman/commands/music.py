import re
import os
import hikari
import asyncio
import logging
import lavalink
import lightbulb
import typing as t

from views.music_view import MusicPlayerView

plugin = lightbulb.Plugin("music")
plugin.description = "Music commands for playing audio in voice channels"
logger = logging.getLogger(__name__)

url_rx = re.compile(r'https?://(?:www\.)?.+')

# Global variables
lavalink_client = None
active_views = {}

class LavalinkEvents:
    @lavalink.listener(lavalink.TrackStartEvent)
    async def track_start(self, event: lavalink.TrackStartEvent):
        player = lavalink_client.player_manager.get(event.player.guild_id)
        if not player:
            return

        channel_id = player.fetch('channel')
        if not channel_id:
            return

        channel = plugin.bot.cache.get_guild_channel(channel_id)
        if channel:
            await plugin.bot.rest.create_message(
                channel=channel_id,
                embed=hikari.Embed(
                    title="Now Playing",
                    description=f"🎵 {event.track.title} by {event.track.author}",
                    color=hikari.Color(0x3498db)
                )
            )

    @lavalink.listener(lavalink.QueueEndEvent)
    async def queue_end(self, event: lavalink.QueueEndEvent):
        guild_id = event.player.guild_id
        await plugin.bot.update_voice_state(guild_id, None)
        if guild_id in active_views:
            del active_views[guild_id]

class LavalinkClient(lavalink.Client):
    def __init__(self, bot_id: int):
        super().__init__(bot_id)
        self.event_manager = LavalinkEvents()
        
    @property
    def bot(self) -> lightbulb.BotApp:
        return plugin.bot

    async def get_guild_gateway_connection_info(self, guild_id: int) -> t.Tuple[str, str]:
        """Get gateway connection info for a guild."""
        voice_state = self.bot.cache.get_voice_state(guild_id, self.bot.get_me().id)
        if voice_state:
            session_id = voice_state.session_id
            server_id = voice_state.session_id  # You might need to get this from somewhere else
            return str(session_id), str(server_id)
        return '', ''

    def register_event_listeners(self):
        """Register lavalink event listeners"""
        self.add_event_hooks(self.event_manager)
        
    async def connect_to_voice(self, guild_id: int, channel_id: int):
        """Create a voice connection."""
        ws = self.bot._voice_states_for_guild.get(guild_id)
        if not ws:
            await asyncio.sleep(0.5)
            return False
        return True
    
async def on_track_start(event: lavalink.TrackStartEvent) -> None:
    player = lavalink_client.player_manager.get(event.guild_id)
    if not player:
        return

    channel_id = player.fetch('channel')
    if not channel_id:
        return

    channel = plugin.bot.cache.get_guild_channel(channel_id)
    if channel:
        await channel.send(
            embed=hikari.Embed(
                title="Now Playing",
                description=f"🎵 {event.track.title} by {event.track.author}",
                color=hikari.Color(0x3498db)
            )
        )

async def on_queue_end(event: lavalink.QueueEndEvent) -> None:
    player = lavalink_client.player_manager.get(event.guild_id)
    if player:
        await plugin.bot.update_voice_state(event.guild_id, None)
        if event.guild_id in active_views:
            del active_views[event.guild_id]

@plugin.listener(hikari.VoiceStateUpdateEvent)
async def voice_state_update(event: hikari.VoiceStateUpdateEvent) -> None:
    if lavalink_client:
        await lavalink_client.voice_update_handler(
            {
                't': 'VOICE_STATE_UPDATE',
                'd': {
                    'guild_id': str(event.guild_id),
                    'user_id': str(event.state.user_id),
                    'session_id': str(event.state.session_id),
                    'channel_id': str(event.state.channel_id) if event.state.channel_id else None
                }
            }
        )

@plugin.listener(hikari.VoiceServerUpdateEvent)
async def voice_server_update(event: hikari.VoiceServerUpdateEvent) -> None:
    if lavalink_client:
        await lavalink_client.voice_update_handler(
            {
                't': 'VOICE_SERVER_UPDATE',
                'd': {
                    'guild_id': str(event.guild_id),
                    'token': event.token,
                    'endpoint': event.endpoint
                }
            }
        )

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
    channel = ctx.get_guild().get_channel(channel_id)
    
    if not channel:
        await ctx.respond("Could not find your voice channel!")
        return

    # Check for permissions
    permissions = lightbulb.utils.permissions_in(channel, ctx.get_guild().get_my_member())
    if not (permissions & hikari.Permissions.CONNECT):
        await ctx.respond("I don't have permission to join your voice channel!")
        return

    try:
        # Create player for guild
        player = lavalink_client.player_manager.create(ctx.guild_id)
        player.store('channel', ctx.channel_id)
        player.store('guild', ctx.guild_id)

        await ctx.bot.update_voice_state(ctx.guild_id, channel_id, self_deaf=True)
        
        # Wait for voice connection to be established
        tries = 0
        while not player.is_connected and tries < 5:
            await asyncio.sleep(0.5)
            tries += 1
        
        if not player.is_connected:
            await ctx.respond("Failed to establish voice connection. Please try again.")
            return

        await ctx.respond(f"Joined <#{channel_id}>!")
    except Exception as e:
        await ctx.respond(f"Failed to join voice channel: {str(e)}")

@plugin.command
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.option("query", "The song to play", type=str, required=True)
@lightbulb.command("play", "Play a song")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def play(ctx: lightbulb.Context) -> None:
    query = ctx.options.query.strip('<>')
    
    if not url_rx.match(query):
        query = f'ytsearch:{query}'

    # Get player and join voice if needed
    player = lavalink_client.player_manager.get(ctx.guild_id)
    if not player or not player.is_connected:
        await join.callback(ctx)
        player = lavalink_client.player_manager.get(ctx.guild_id)
        
        if not player or not player.is_connected:
            await ctx.respond("Failed to establish voice connection. Please try again.")
            return
    
    try:
        results = await player.node.get_tracks(query)
        if not results or not results.tracks:
            return await ctx.respond("No results found!")

        embed = hikari.Embed(color=hikari.Color(0x3498db))

        if results.load_type == lavalink.LoadType.PLAYLIST:
            tracks = results.tracks
            for track in tracks:
                player.add(requester=ctx.author.id, track=track)

            embed.title = "Playlist Enqueued!"
            embed.description = f"{results.playlist_info.name} - {len(tracks)} tracks"
        else:
            track = results.tracks[0]
            embed.title = "Track Enqueued"
            embed.description = f"[{track.title}]({track.uri})"
            player.add(requester=ctx.author.id, track=track)

        await ctx.respond(embed=embed)

        # Create player view if not exists
        if ctx.guild_id not in active_views:
            view = MusicPlayerView(player)
            msg = await ctx.respond(
                embed=hikari.Embed(
                    title="Music Player",
                    description=f"Now Playing: {track.title}\n\nUse the controls below to control playback",
                    color=hikari.Color(0x3498db)
                ),
                components=view.build()
            )
            active_views[ctx.guild_id] = view
            ctx.bot.d.miru.start_view(view)

        if not player.is_playing:
            await player.play()
    except Exception as e:
        await ctx.respond(f"An error occurred: {str(e)}")

@plugin.command
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.option("strength", "Filter strength (0-100)", type=float, required=True)
@lightbulb.command("lowpass", "Set the strength of the low pass filter")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def lowpass(ctx: lightbulb.Context) -> None:
    player = lavalink_client.player_manager.get(ctx.guild_id)
    if not player:
        await ctx.respond("Not connected to a voice channel!")
        return

    strength = max(0.0, min(100.0, ctx.options.strength))
    
    if strength == 0.0:
        await player.remove_filter('lowpass')
        await ctx.respond(
            embed=hikari.Embed(
                title="Low Pass Filter",
                description="Disabled Low Pass Filter",
                color=hikari.Color(0x3498db)
            )
        )
        return

    low_pass = lavalink.LowPass()
    low_pass.update(smoothing=strength)
    await player.set_filter(low_pass)
    
    await ctx.respond(
        embed=hikari.Embed(
            title="Low Pass Filter",
            description=f"Set Low Pass Filter strength to {strength}",
            color=hikari.Color(0x3498db)
        )
    )

@plugin.command
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("leave", "Leave the voice channel")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def leave(ctx: lightbulb.Context) -> None:
    player = lavalink_client.player_manager.get(ctx.guild_id)
    if not player:
        await ctx.respond("Not connected to a voice channel!")
        return

    player.queue.clear()
    await player.stop()
    await ctx.bot.update_voice_state(ctx.guild_id, None)
    
    if ctx.guild_id in active_views:
        del active_views[ctx.guild_id]
    
    await ctx.respond("✅ Disconnected and cleared queue!")

@plugin.command
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("queue", "Show the current queue")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def queue(ctx: lightbulb.Context) -> None:
    player = lavalink_client.player_manager.get(ctx.guild_id)
    
    if not player or not player.queue:
        await ctx.respond("The queue is empty!")
        return
        
    embed = hikari.Embed(
        title="Music Queue",
        color=hikari.Color(0x3498db)
    )
    
    if player.current:
        embed.add_field(
            name="Now Playing",
            value=f"🎵 {player.current.title}",
            inline=False
        )
    
    queue_list = []
    for idx, track in enumerate(player.queue, 1):
        queue_list.append(f"{idx}. {track.title}")
    
    if queue_list:
        embed.add_field(
            name="Up Next",
            value="\n".join(queue_list[:10]),
            inline=False
        )
        
        if len(queue_list) > 10:
            embed.set_footer(text=f"And {len(queue_list) - 10} more...")
    
    await ctx.respond(embed=embed)

@plugin.listener(hikari.StartedEvent)
async def on_ready(event: hikari.StartedEvent) -> None:
    """Initialize Lavalink client when the bot is ready."""
    global lavalink_client
    
    await asyncio.sleep(2)
    
    if not lavalink_client:
        bot_id = plugin.bot.get_me().id
        lavalink_client = LavalinkClient(bot_id)
        
        try:
            lavalink_client.add_node(
                host=os.getenv("LAVALINK_SERVER_HOST", "lavalink"),
                port=int(os.getenv("LAVALINK_SERVER_PORT", 2333)),
                password=os.getenv("LAVALINK_SERVER_PASSWORD", "youshallnotpass"),
                region="us",
                name="default-node",
            )
            
            logger.info(f"Successfully connected to Lavalink node")
            lavalink_client.register_event_listeners()
        except Exception as e:
            logger.error(f"Failed to connect to Lavalink node: {e}")

def load(bot: lightbulb.BotApp) -> None:
    global active_views
    active_views = {}
    bot.add_plugin(plugin)

def unload(bot: lightbulb.BotApp) -> None:
    if lavalink_client:
        lavalink_client.destroy()
    bot.remove_plugin(plugin)