import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.models import FuelType
from src.services.ministry_api import MinistryAPIClient
from src.services.finder import FuelStationFinder

logger = logging.getLogger(__name__)

# Conversation states
LOCATION, FUEL_TYPE, RADIUS = range(3)

async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle user's location and ask for fuel type"""
    logger.info(f"📍 location_handler called! Update: {update}")
    user_location = update.message.location

    context.user_data['latitude'] = user_location.latitude
    context.user_data['longitude'] = user_location.longitude

    keyboard = []
    for fuel_type in FuelType:
        keyboard.append([InlineKeyboardButton(
            fuel_type.value,
            callback_data=f"fuel_{fuel_type.value}"
        )])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "⛽ ¿Qué tipo de combustible buscas?",
        reply_markup=reply_markup
    )

    return FUEL_TYPE

async def fuel_type_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle fuel type selection and ask for radius"""
    query = update.callback_query
    await query.answer()

    fuel_type = query.data.replace("fuel_", "")
    context.user_data['fuel_type'] = fuel_type

    await query.edit_message_text(
        f"✅ Combustible seleccionado: *{fuel_type}*\n\n"
        "📏 Ahora indica el radio de búsqueda en kilómetros.\n\n"
        "Ejemplos: 5, 10, 20",
        parse_mode='Markdown'
    )

    return RADIUS

async def radius_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle radius input and find cheapest stations"""
    radius_text = update.message.text.strip()

    try:
        radius = float(radius_text)
        if radius <= 0 or radius > 100:
            await update.message.reply_text(
                "❌ El radio debe estar entre 1 y 100 km. Intenta de nuevo."
            )
            return RADIUS
    except ValueError:
        await update.message.reply_text(
            "❌ Por favor, ingresa un número válido. Ejemplo: 5, 10, 20"
        )
        return RADIUS

    lat = context.user_data.get('latitude')
    lon = context.user_data.get('longitude')
    fuel_type_str = context.user_data.get('fuel_type')

    if not all([lat, lon, fuel_type_str]):
        await update.message.reply_text(
            "❌ Error en los datos. Por favor, empieza de nuevo con /start"
        )
        return ConversationHandler.END

    try:
        fuel_type = FuelType(fuel_type_str)
    except ValueError:
        await update.message.reply_text(
            "❌ Tipo de combustible inválido. Empieza de nuevo con /start"
        )
        return ConversationHandler.END

    status_message = await update.message.reply_text(
        "🔍 Buscando las gasolineras más baratas...\n\n"
        "Esto puede tardar unos segundos."
    )

    try:
        api_client = MinistryAPIClient()
        all_stations = await api_client.get_all_stations()

        finder = FuelStationFinder()
        stations = await finder.find_cheapest(
            stations=all_stations,
            user_lat=lat,
            user_lon=lon,
            radius_km=radius,
            fuel_type=fuel_type
        )

        await status_message.delete()

        if not stations:
            await update.message.reply_text(
                f"❌ No encontré gasolineras con {fuel_type_str} "
                f"en un radio de {radius} km.\n\n"
                "💡 Intenta con un radio mayor.",
                reply_markup=get_restart_keyboard()
            )
        else:
            await send_results(update, stations, fuel_type)

    except Exception as e:
        await status_message.delete()
        await update.message.reply_text(
            f"❌ Error al buscar gasolineras: {str(e)}\n\n"
            "Por favor, intenta más tarde o usa /start para empezar de nuevo."
        )

    context.user_data.clear()
    return ConversationHandler.END

async def send_results(update: Update, stations, fuel_type: FuelType) -> None:
    """Send search results to user"""
    message = f"⛽ *Las {len(stations)} gasolineras más baratas*\n\n"

    for i, station in enumerate(stations, 1):
        distance = getattr(station, '_distance', 0.0)
        price = station.precios[fuel_type]

        message += (
            f"*{i}. {station.rotulo}*\n"
            f"💰 Precio: *{price:.3f} €/l*\n"
            f"📍 {station.direccion}\n"
            f"🏘️ {station.municipio}, {station.provincia}\n"
            f"📏 Distancia: {distance:.2f} km\n\n"
        )

    message += "✅ Datos oficiales del Ministerio de Industria y Turismo"

    await update.message.reply_text(
        message,
        parse_mode='Markdown',
        reply_markup=get_restart_keyboard()
    )

def get_restart_keyboard():
    """Create keyboard with restart button"""
    from telegram import ReplyKeyboardMarkup, KeyboardButton

    keyboard = [[KeyboardButton("/start")]]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
