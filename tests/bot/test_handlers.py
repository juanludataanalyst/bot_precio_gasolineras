import pytest
from unittest.mock import Mock, AsyncMock, patch
from telegram import Update, User, Chat, Location
from telegram.ext import ContextTypes
from src.bot.handlers import start_command, help_command, cancel_command

@pytest.mark.asyncio
async def test_start_command():
    """Test /start command sends welcome message"""
    update = Mock(spec=Update)
    update.message = AsyncMock()
    update.message.reply_text = AsyncMock()

    context = Mock(spec=ContextTypes.DEFAULT_TYPE)

    await start_command(update, context)

    update.message.reply_text.assert_called_once()
    args = update.message.reply_text.call_args[0]
    assert "ubicación" in args[0].lower()

@pytest.mark.asyncio
async def test_cancel_command():
    """Test /cancel command cancels conversation"""
    update = Mock(spec=Update)
    update.message = AsyncMock()
    update.message.reply_text = AsyncMock()

    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}

    await cancel_command(update, context)

    update.message.reply_text.assert_called_once()
    assert context.user_data == {}
