import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from src.bot import handlers, conversation

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

import os
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

def main() -> None:
    """Start the bot"""
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", handlers.start_command))
    application.add_handler(CommandHandler("help", handlers.help_command))
    application.add_handler(CommandHandler("cancel", handlers.cancel_command))

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", handlers.start_command)],
        states={
            conversation.LOCATION: [
                MessageHandler(filters.LOCATION, conversation.location_handler)
            ],
            conversation.FUEL_TYPE: [
                CallbackQueryHandler(conversation.fuel_type_callback)
            ],
            conversation.RADIUS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, conversation.radius_handler)
            ],
        },
        fallbacks=[CommandHandler("cancel", handlers.cancel_command)],
    )

    application.add_handler(conv_handler)

    # Start the bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
