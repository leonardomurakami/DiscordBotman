import datetime
import logging
import hikari

logger = logging.getLogger(__name__)

class MessageHandler:
    """Handles message-related events."""
    
    def __init__(self, bot):
        self.bot = bot

    async def on_message_delete(self, event: hikari.GuildMessageDeleteEvent) -> None:
        """Handle message delete events."""
        if not event.old_message:
            return
            
        message_data = {
            "guild_id": str(event.guild_id),
            "channel_id": str(event.channel_id),
            "message_id": str(event.message_id),
            "content": event.old_message.content,
            "author_id": str(event.old_message.author.id) if event.old_message.author else None
        }
        
        await self.bot.d.api_client.store_deleted_message(message_data)

    async def on_message_edit(self, event: hikari.GuildMessageUpdateEvent) -> None:
        """Handle message edit events."""
        if not event.old_message or not event.message:
            return
            
        message_data = {
            "guild_id": str(event.guild_id),
            "channel_id": str(event.channel_id),
            "message_id": str(event.message_id),
            "old_content": event.old_message.content,
            "new_content": event.message.content,
            "author_id": str(event.author_id) if event.author_id else None
        }
        
        await self.bot.d.api_client.store_edited_message(message_data)