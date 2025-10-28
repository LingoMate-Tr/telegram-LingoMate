# bot.py
import logging
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
)
from config import TOKEN, LOG_FORMAT, LOG_LEVEL
from bot_handlers import start, button, translate_text, translate_image, translate_audio, translate_document
from database import initialize_database

logging.basicConfig(
    format=LOG_FORMAT,
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO)
)
logger = logging.getLogger(__name__)

def main():
    if not TOKEN:
        logger.error("TOKEN environment variable not set!")
        return

    initialize_database()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_text))
    app.add_handler(MessageHandler(filters.PHOTO, translate_image))
    app.add_handler(MessageHandler(filters.AUDIO, translate_audio))
    app.add_handler(MessageHandler(filters.Document.PDF, translate_document))

    logger.info("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
