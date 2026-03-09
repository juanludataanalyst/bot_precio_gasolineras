import logging
import os
import asyncio
import threading
import time
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler, ContextTypes
from src.bot import handlers, conversation
from aiohttp import web

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
PORT = int(os.getenv("PORT", "8000"))

async def health_check(request):
    """Health check endpoint for Koyeb"""
    return web.Response(text="OK", status=200)

async def root(request):
    """Root endpoint"""
    return web.Response(text="Bot is running", status=200)

def start_web_server_sync():
    """Start web server in a separate thread synchronously"""
    # Create new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def run_server():
        app = web.Application()
        app.router.add_get("/", root)
        app.router.add_get("/health", health_check)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', PORT)
        await site.start()
        logger.info(f"Web server started on port {PORT}")

        # Keep the server running
        try:
            while True:
                await asyncio.sleep(3600)
        except asyncio.CancelledError:
            await runner.cleanup()

    # Run the server
    loop.run_until_complete(run_server())

def main():
    """Run the bot in main thread with web server in background"""
    # Start web server in a separate thread
    logger.info("Starting web server in background thread...")
    web_thread = threading.Thread(target=start_web_server_sync, daemon=True)
    web_thread.start()

    # Give web server time to start
    time.sleep(2)

    # Create the bot application
    application = Application.builder().token(TOKEN).build()

    # Add conversation handler (includes /start as entry_point)
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
        allow_reentry=True,
    )

    application.add_handler(conv_handler)

    # Add other command handlers (help, cancel)
    application.add_handler(CommandHandler("help", handlers.help_command))
    application.add_handler(CommandHandler("cancel", handlers.cancel_command))

    # Add error handler to catch exceptions
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
        logger.error(f"Exception while handling an update: {context.error}")

    application.add_error_handler(error_handler)

    # Add other command handlers (help, cancel)
    application.add_handler(CommandHandler("help", handlers.help_command))

    logger.info("✅ Bot and web server are running")

    # Start the bot (this is blocking and runs in main thread)
    logger.info("Starting bot...")
    application.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == "__main__":
    main()
