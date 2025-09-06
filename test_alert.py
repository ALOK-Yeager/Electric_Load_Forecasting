#!/usr/bin/env python3
"""
Test Alert Script for Electric Load Forecasting

This script tests the Telegram notification functionality without running the full forecasting pipeline.
It's a quick way to verify that your bot token and chat ID are configured correctly.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Check if the required environment variables are set
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    logger.error("Missing environment variables. Make sure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are set in your .env file.")
    logger.info("See the README.md for instructions on setting up your Telegram bot.")
    sys.exit(1)

# Try to import the notification module
try:
    # Add the project root to the path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Try import from legacy location first
    try:
        from notification import send_forecast_alert
    except ImportError:
        # Try the new location
        from utils.telegram_notifier import TelegramNotifier
        
        # Create a wrapper to maintain compatibility
        async def send_forecast_alert(model_name, error_value, message=None):
            notifier = TelegramNotifier()
            level = "critical" if error_value > 10.0 else "error"
            try:
                await notifier.send_alert(
                    message=message or "Forecast error exceeds acceptable threshold. Manual review recommended.",
                    error_level=level,
                    model_name=model_name,
                    error_value=error_value
                )
                return True
            except Exception as e:
                logger.error(f"Error sending alert: {e}")
                return False
except ImportError as e:
    logger.error(f"Could not import notification module: {e}")
    logger.info("Make sure you have installed all the required packages from requirements.txt")
    sys.exit(1)

async def test_notification():
    """Send a test notification to verify functionality"""
    logger.info("Sending test forecast alert...")
    
    # Test values
    model_name = "ARIMA"
    error_value = 8.75
    message = "This is a test alert from the Electric Load Forecasting system."
    
    try:
        result = await send_forecast_alert(model_name, error_value, message)
        
        if result:
            logger.info("✅ Test alert sent successfully! Check your Telegram.")
            if BOT_TOKEN:
                logger.info(f"   Bot Token: ...{BOT_TOKEN[-4:]} (last 4 characters)")
            logger.info(f"   Chat ID: {CHAT_ID}")
            return True
        else:
            logger.error("❌ Failed to send test alert.")
            return False
    except Exception as e:
        logger.error(f"❌ Error sending test alert: {e}")
        return False

if __name__ == "__main__":
    if sys.platform.startswith("win"):
        # Windows requires this to properly handle asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Run the test
    success = asyncio.run(test_notification())
    
    if not success:
        logger.info("\nTroubleshooting tips:")
        logger.info("1. Double-check your BOT_TOKEN and CHAT_ID in the .env file")
        logger.info("2. Make sure you've started a conversation with your bot")
        logger.info("3. Check your internet connection")
        logger.info("4. Make sure you've installed python-telegram-bot: pip install python-telegram-bot")
        sys.exit(1)