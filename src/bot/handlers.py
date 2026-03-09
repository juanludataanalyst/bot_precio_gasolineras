import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from src.bot import conversation

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask for location"""
    chat_id = update.effective_chat.id if update.effective_chat else "Unknown"
    message_text = update.effective_message.text if update.effective_message else "None"
    logger.info(f"🎯 start_command called! Chat ID: {chat_id}, Message: {message_text}")

    try:
        await update.message.reply_text(
            "👋 ¡Hola! Soy el bot de precios de gasolineras.\n\n"
            "Para encontrar las gasolineras más baratas cerca de ti, "
            "necesito que me compartas tu ubicación.\n\n"
            "📍 Pulsa el clip 📎 y selecciona 'Ubicación' o usa el botón de ubicación.",
            reply_markup=get_location_keyboard()
        )
        logger.info("✅ Reply sent successfully")
        return conversation.LOCATION
    except Exception as e:
        logger.error(f"❌ Error in start_command: {e}")
        raise

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message"""
    help_text = (
        "🤖 *Ayuda del Bot*\n\n"
        "Para encontrar las gasolineras más baratas:\n"
        "1. Pulsa /start para comenzar\n"
        "2. Comparte tu ubicación GPS\n"
        "3. Selecciona el tipo de combustible\n"
        "4. Indica el radio de búsqueda en km\n\n"
        "Comandos disponibles:\n"
        "/start - Iniciar búsqueda\n"
        "/help - Mostrar esta ayuda\n"
        "/cancel - Cancelar búsqueda"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation"""
    await update.message.reply_text(
        "❌ Búsqueda cancelada. Pulsa /start para comenzar de nuevo."
    )
    context.user_data.clear()
    return ConversationHandler.END

def get_location_keyboard():
    """Create keyboard with location button"""
    from telegram import ReplyKeyboardMarkup, KeyboardButton

    keyboard = [
        [KeyboardButton("📍 Compartir mi ubicación", request_location=True)]
    ]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
