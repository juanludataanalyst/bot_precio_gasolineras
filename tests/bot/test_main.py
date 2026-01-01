import pytest
from unittest.mock import Mock, patch
from telegram import Update
from telegram.ext import Application
from src.bot.main import main

def test_main_creates_application():
    """Test that main function creates and configures the application"""
    with patch('src.bot.main.Application') as mock_app_class, \
         patch('src.bot.main.logger') as mock_logger:

        # Mock the Application builder
        mock_builder = Mock()
        mock_app_class.builder.return_value = mock_builder
        mock_builder.token.return_value = mock_builder
        mock_builder.build.return_value = Mock()

        # Mock the application instance
        mock_application = Mock()
        mock_builder.build.return_value = mock_application

        # Run main (will try to start polling, so we need to catch that)
        mock_application.run_polling.side_effect = KeyboardInterrupt()

        # Execute and catch KeyboardInterrupt
        try:
            main()
        except KeyboardInterrupt:
            pass

        # Verify Application was built with token
        mock_app_class.builder.assert_called_once()
        mock_builder.token.assert_called_once()

        # Verify handlers were added
        assert mock_application.add_handler.call_count == 4  # 3 commands + 1 conversation

        # Verify bot started
        mock_logger.info.assert_called_with("Starting bot...")
        mock_application.run_polling.assert_called_once()

