import logging
import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler, ContextTypes
from src.bot import handlers, conversation
from aiohttp import web
from concurrent.futures import ThreadPoolExecutor

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

async def start_web_server():
    """Start a simple web server for health checks"""
    app = web.Application()
    app.router.add_get("/", root)
    app.router.add_get("/health", health_check)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logger.info(f"Web server started on port {PORT}")

    # Keep the runner alive
    return runner

def run_bot():
    """Run the Telegram bot (blocking)"""
    """Start the Telegram bot"""
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

    # Add debug handler to see all messages
    async def debug_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info(f"🔍 Unhandled update: {update}")

    application.add_handler(MessageHandler(filters.ALL, debug_handler))

    # Add other command handlers (help, cancel)
    application.add_handler(CommandHandler("help", handlers.help_command))

    # Start the bot (blocking call)
    logger.info("Starting bot...")
    application.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )

async def main():
    """Run both the web server and the bot"""
    try:
        # Start the web server
        web_runner = await start_web_server()

        # Start the bot in a separate thread
        logger.info("Starting bot in background thread...")
        import threading
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()

        logger.info("✅ Bot and web server are running")

        # Keep the web server alive
        try:
            # Just keep the event loop alive
            while True:
                await asyncio.sleep(3600)  # Sleep for 1 hour at a time
        except (KeyboardInterrupt, SystemExit):
            logger.info("Received shutdown signal")
        finally:
            # Cleanup
            logger.info("Shutting down...")
            await web_runner.cleanup()

    except Exception as e:
        logger.error(f"Error starting application: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
