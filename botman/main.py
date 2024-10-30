import logging
from bot import Bot

logger = logging.getLogger(__name__)

def main():
    """Main entry point for the bot."""
    try:
        bot = Bot()
        bot.run()
    except Exception as e:
        logger.critical(f"Failed to start bot: {e}")
        raise

if __name__ == "__main__":
    main()