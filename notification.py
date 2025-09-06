"""
Telegram notification script for Electric Load Forecasting
This module provides async functions to send notifications via Telegram
"""

import os
import asyncio
import logging
from datetime import datetime
from telegram import Bot
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get Telegram token and chat ID from environment variables with defaults to prevent None
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')

# Check if tokens are available
if not TELEGRAM_BOT_TOKEN:
    logger.error("Missing Telegram bot token. Set TELEGRAM_BOT_TOKEN environment variable.")
if not TELEGRAM_CHAT_ID:
    logger.error("Missing Telegram chat ID. Set TELEGRAM_CHAT_ID environment variable.")

async def send_forecast_alert(model_name, error_value, message=None):
    """
    Send a forecast alert notification via Telegram
    
    Args:
        model_name (str): Name of the forecasting model
        error_value (float): Error percentage value
        message (str, optional): Additional message
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("Cannot send notification: Missing Telegram credentials")
        return False
    
    # Format the current time
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Determine emoji and severity based on error value
    if error_value > 10:
        emoji = "🚨"
        severity = "Critical"
    elif error_value > 5:
        emoji = "⚠️"
        severity = "Warning"
    else:
        emoji = "ℹ️"
        severity = "Info"
    
    # Format the message
    text = f"{emoji} *{severity} Forecast Alert* {emoji}\n\n"
    text += f"*Model:* `{model_name}`\n"
    text += f"*Error:* `{error_value:.2f}%`\n\n"
    
    if message:
        text += f"{message}\n\n"
    
    text += f"*Time:* `{timestamp}`"
    
    try:
        # Make sure token is not None
        if not TELEGRAM_BOT_TOKEN:
            logger.error("Cannot send notification: Bot token is None")
            return False
            
        # Initialize bot and send message
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        if not TELEGRAM_CHAT_ID:
            logger.error("Cannot send notification: Chat ID is None")
            return False
            
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=text,
            parse_mode="Markdown"
        )
        logger.info(f"Sent {severity.lower()} notification for {model_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to send notification: {str(e)}")
        return False

async def send_test_message(custom_message=None):
    """Send a test message to verify Telegram configuration"""
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        message = custom_message or "🔄 This is a test message from the Electric Load Forecasting system."
        
        if not TELEGRAM_CHAT_ID:
            logger.error("Cannot send test: Missing chat ID")
            return False
            
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message
        )
        logger.info("Test message sent successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to send test message: {str(e)}")
        return False

async def main():
    """Main function for testing the notification system"""
    import sys
    
    if len(sys.argv) > 1:
        model = sys.argv[1]
        error = float(sys.argv[2]) if len(sys.argv) > 2 else 7.5
        message = sys.argv[3] if len(sys.argv) > 3 else "This is a test alert."
        
        logger.info(f"Sending test alert for {model} with {error}% error")
        result = await send_forecast_alert(model, error, message)
    else:
        logger.info("Sending basic test message")
        result = await send_test_message()
    
    if result:
        print("✅ Notification sent successfully!")
    else:
        print("❌ Failed to send notification")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())