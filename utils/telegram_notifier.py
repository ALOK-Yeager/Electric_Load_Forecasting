"""
Telegram Notification System for Load Forecasting

This module provides a TelegramNotifier class to send alerts about
forecasting performance and system status to a Telegram channel.
"""

import os
import logging
import requests
from datetime import datetime
import pytz
from dotenv import load_dotenv


class TelegramNotifier:
    """
    A class to handle sending notifications to a Telegram chat via Telegram Bot API.
    
    Attributes:
        token (str): Telegram Bot API token
        chat_id (str): Telegram chat ID to send messages to
        timezone (str): Timezone for message timestamps (default: 'Asia/Kolkata')
    """
    
    def __init__(self, token=None, chat_id=None, timezone='Asia/Kolkata'):
        """
        Initialize the TelegramNotifier with bot token and chat ID.
        
        Args:
            token (str, optional): Telegram Bot API token. If None, will try to load from environment.
            chat_id (str, optional): Telegram chat ID. If None, will try to load from environment.
            timezone (str, optional): Timezone for timestamps. Defaults to 'Asia/Kolkata'.
        """
        # Load environment variables if not already loaded
        load_dotenv()
        
        # Get token and chat_id from parameters or environment variables
        self.token = token or os.environ.get('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.environ.get('TELEGRAM_CHAT_ID')
        self.timezone = timezone
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Validate token and chat_id
        if not self.token or not self.chat_id:
            self.logger.error("Missing Telegram token or chat_id. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables.")
            raise ValueError("Missing Telegram token or chat_id")
            
        # Fix any token formatting issues
        self._validate_and_fix_token()
    
    def _validate_and_fix_token(self):
        """Validate and fix common token format issues"""
        if not self.token:
            return
            
        # Check if token appears to be duplicated (contains more than one colon)
        if self.token.count(':') > 1:
            self.logger.warning("Token format issue detected - appears to be duplicated. Attempting to fix...")
            # Extract the first valid token pattern (format: numbers:letters)
            parts = self.token.split(':')
            if len(parts) >= 2:
                # Take the first number part and the first letter part
                self.token = f"{parts[0]}:{parts[1].split(':')[0]}"
                self.logger.info("Token format fixed")
                
        # Verify basic format: numbers:letters
        if not ':' in self.token:
            self.logger.warning("Token doesn't contain required format (numbers:letters)")
    
    def send_alert(self, message, error_level='info', model_name=None, error_value=None):
        """
        Send formatted alert message with timestamp to Telegram chat.
        
        Args:
            message (str): The alert message to send
            error_level (str, optional): Level of alert ('info', 'warning', 'error', 'critical'). Defaults to 'info'.
            model_name (str, optional): Name of the forecasting model. Defaults to None.
            error_value (float, optional): Error value/percentage to report. Defaults to None.
            
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        # Create emoji based on error level
        emoji_map = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '🚨',
            'critical': '🔥'
        }
        emoji = emoji_map.get(error_level.lower(), 'ℹ️')
        
        # Get current timestamp in the specified timezone
        now = datetime.now(pytz.timezone(self.timezone))
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S %Z")
        
        # Format the message
        formatted_message = f"{emoji} *Load Forecasting Alert* {emoji}\n\n"
        
        if model_name:
            formatted_message += f"*Model:* `{model_name}`\n"
        
        if error_value is not None:
            formatted_message += f"*Forecast Error:* `{error_value:.2f}%`\n\n"
            
        formatted_message += f"{message}\n\n"
        formatted_message += f"*Time:* `{timestamp}`"
        
        # Send the message
        return self._send_message(formatted_message)
    
    def test_connection(self):
        """
        Test the connection to the Telegram API by sending a test message.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        message = "🔄 *Connection Test*\n\nThis is a test message from the Electric Load Forecasting system."
        result = self._send_message(message)
        
        if result:
            self.logger.info("Telegram connection test successful")
        else:
            self.logger.error("Telegram connection test failed")
            
        return result
    
    def _send_message(self, message):
        """
        Send a message to the Telegram chat.
        
        Args:
            message (str): The message to send
            
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        api_url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        
        params = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        try:
            # Log the request URL for debugging (mask token partially)
            masked_token = self.token[:5] + "..." + self.token[-5:] if len(self.token) > 10 else "***masked***"
            self.logger.debug(f"Sending request to: https://api.telegram.org/bot{masked_token}/sendMessage")
            
            response = requests.post(api_url, json=params, timeout=10)
            response.raise_for_status()
            
            # Log success
            self.logger.info(f"Message sent to Telegram chat {self.chat_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            # Handle network/API errors
            self.logger.error(f"Failed to send Telegram message: {str(e)}")
            return False
        except Exception as e:
            # Handle any other unexpected errors
            self.logger.error(f"Unexpected error sending Telegram message: {str(e)}")
            return False

# Example usage
if __name__ == "__main__":
    # Set up basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Create notifier instance
        notifier = TelegramNotifier()
        
        # Test the connection
        if notifier.test_connection():
            print("Connection test successful!")
            
            # Send a sample high error alert
            notifier.send_alert(
                message="Manual review recommended.",
                error_level="error",
                model_name="ARIMA",
                error_value=8.75
            )
    except ValueError as e:
        print(f"Error: {str(e)}")
        print("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables.")