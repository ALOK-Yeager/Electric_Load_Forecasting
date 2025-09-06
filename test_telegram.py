#!/usr/bin/env python3
"""
Test script for the Telegram notification system
Used to verify alert functionality for load forecasting
"""
import os
import logging
import argparse
from dotenv import load_dotenv
from utils.telegram_notifier import TelegramNotifier

def setup_logging():
    """Configure basic logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_notification(error_value=None, model_name=None):
    """
    Test the Telegram notification system
    
    Args:
        error_value (float): Optional error value to include in test
        model_name (str): Optional model name to include in test
    """
    # Load environment variables
    load_dotenv()
    
    # Check if environment variables are set
    if not os.environ.get('TELEGRAM_BOT_TOKEN') or not os.environ.get('TELEGRAM_CHAT_ID'):
        print("Error: Missing Telegram credentials.")
        print("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env file.")
        print("\nExample .env file contents:")
        print('TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN_HERE"')
        print('TELEGRAM_CHAT_ID="YOUR_CHAT_ID_HERE"')
        return False
    
    try:
        # Create notifier instance
        notifier = TelegramNotifier()
        
        # Test the connection first
        if notifier.test_connection():
            print("✅ Connection to Telegram API successful!")
            
            # If error_value is provided, send a sample alert
            if error_value is not None:
                try:
                    error_value = float(error_value)
                    error_level = "error" if error_value > 5.0 else "info"
                    message = "Manual review recommended." if error_value > 5.0 else "Forecasting within acceptable range."
                    
                    print(f"Sending sample alert with {error_value}% error...")
                    success = notifier.send_alert(
                        message=message,
                        error_level=error_level,
                        model_name=model_name or "ARIMA",
                        error_value=error_value
                    )
                    
                    if success:
                        print("✅ Alert sent successfully! Check your Telegram.")
                    else:
                        print("❌ Failed to send alert. Message queued for retry.")
                        
                    # Process any queued messages
                    notifier.process_queue()
                except ValueError:
                    print("❌ Error: Invalid error_value. Must be a number.")
            
            return True
        else:
            print("❌ Failed to connect to Telegram API.")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Test the Telegram notification system")
    parser.add_argument("--error", type=float, help="Sample error percentage to include in test")
    parser.add_argument("--model", type=str, help="Model name to include in test")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set up logging
    setup_logging()
    
    # Run the test
    test_notification(error_value=args.error, model_name=args.model)