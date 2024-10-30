import datetime
import logging
import hikari

logger = logging.getLogger(__name__)

class MessageHandler:
    """Handles message-related events."""
    
    def __init__(self, bot):
        self.bot = bot

    async def on_message_delete(self, event: hikari.GuildMessageDeleteEvent) -> None:
        """Handle message deletion events."""
        if not event.old_message or event.old_message.author.is_bot:
            return
            
        self.bot.d.deleted_messages[event.channel_id] = {
            'content': event.old_message.content,
            'author': event.old_message.author,
            'time': datetime.datetime.now(),
            'attachments': event.old_message.attachments
        }
        
        logger.debug(
            f"Message deleted in channel {event.channel_id} "
            f"by user {event.old_message.author.username}"
        )

    async def on_message_edit(self, event: hikari.GuildMessageUpdateEvent) -> None:
        """Handle message edit events."""
        if not event.old_message or event.old_message.author.is_bot:
            return
        
        self.bot.d.edited_messages[event.channel_id] = {
            'old_content': event.old_message.content,
            'new_content': event.message.content,
            'author': event.old_message.author,
            'time': datetime.datetime.now()
        }
        
        logger.debug(
            f"Message edited in channel {event.channel_id} "
            f"by user {event.old_message.author.username}"
        )