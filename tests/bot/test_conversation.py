import pytest
from unittest.mock import Mock, AsyncMock, patch
from telegram import Update, User, Chat, Location
from telegram.ext import ContextTypes
from src.bot.conversation import (
    location_handler,
    fuel_type_callback,
    radius_handler,
    LOCATION,
    FUEL_TYPE,
    RADIUS
)

@pytest.mark.asyncio
async def test_location_handler_saves_location():
    """Test that location is saved in user_data"""
    update = Mock(spec=Update)
    update.message = AsyncMock()
    update.message.location = Mock(latitude=40.4168, longitude=-3.7038)
    update.message.reply_text = AsyncMock()

    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}

    result = await location_handler(update, context)

    assert context.user_data['latitude'] == 40.4168
    assert context.user_data['longitude'] == -3.7038
    assert result == FUEL_TYPE
    update.message.reply_text.assert_called_once()

@pytest.mark.asyncio
async def test_fuel_type_callback_saves_fuel_type():
    """Test that fuel type is saved in user_data"""
    update = Mock(spec=Update)
    update.callback_query = AsyncMock()
    update.callback_query.data = "fuel_Gasolina 95 E5"
    update.callback_query.edit_message_text = AsyncMock()

    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}

    result = await fuel_type_callback(update, context)

    assert context.user_data['fuel_type'] == "Gasolina 95 E5"
    assert result == RADIUS
    update.callback_query.answer.assert_called_once()
    update.callback_query.edit_message_text.assert_called_once()

@pytest.mark.asyncio
async def test_radius_handler_valid_radius():
    """Test radius handler with valid input"""
    update = Mock(spec=Update)
    update.message = AsyncMock()
    update.message.text = "10"

    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {
        'latitude': 40.4168,
        'longitude': -3.7038,
        'fuel_type': 'Gasolina 95 E5'
    }

    with patch('src.bot.conversation.MinistryAPIClient') as mock_api_client, \
         patch('src.bot.conversation.FuelStationFinder') as mock_finder_class:

        # Mock the API client
        mock_api_instance = AsyncMock()
        mock_api_instance.get_all_stations.return_value = []
        mock_api_client.return_value = mock_api_instance

        # Mock the finder
        mock_finder_instance = AsyncMock()
        mock_finder_instance.find_cheapest.return_value = []
        mock_finder_class.return_value = mock_finder_instance

        result = await radius_handler(update, context)

        mock_api_instance.get_all_stations.assert_called_once()
        mock_finder_instance.find_cheapest.assert_called_once()
        assert result == -1  # ConversationHandler.END

@pytest.mark.asyncio
async def test_radius_handler_invalid_radius_negative():
    """Test radius handler with negative radius"""
    update = Mock(spec=Update)
    update.message = AsyncMock()
    update.message.text = "-5"

    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {
        'latitude': 40.4168,
        'longitude': -3.7038,
        'fuel_type': 'Gasolina 95 E5'
    }

    result = await radius_handler(update, context)

    assert result == RADIUS
    update.message.reply_text.assert_called_once()
    assert "entre 1 y 100" in update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
async def test_radius_handler_invalid_radius_too_large():
    """Test radius handler with radius > 100"""
    update = Mock(spec=Update)
    update.message = AsyncMock()
    update.message.text = "150"

    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {
        'latitude': 40.4168,
        'longitude': -3.7038,
        'fuel_type': 'Gasolina 95 E5'
    }

    result = await radius_handler(update, context)

    assert result == RADIUS
    update.message.reply_text.assert_called_once()

@pytest.mark.asyncio
async def test_radius_handler_invalid_radius_non_numeric():
    """Test radius handler with non-numeric input"""
    update = Mock(spec=Update)
    update.message = AsyncMock()
    update.message.text = "abc"

    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {
        'latitude': 40.4168,
        'longitude': -3.7038,
        'fuel_type': 'Gasolina 95 E5'
    }

    result = await radius_handler(update, context)

    assert result == RADIUS
    update.message.reply_text.assert_called_once()
    assert "número válido" in update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
async def test_radius_handler_missing_user_data():
    """Test radius handler with missing user data"""
    update = Mock(spec=Update)
    update.message = AsyncMock()
    update.message.text = "10"

    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}  # Missing required data

    result = await radius_handler(update, context)

    assert result == -1  # ConversationHandler.END
    update.message.reply_text.assert_called_once()
