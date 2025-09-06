#!/usr/bin/env python3
"""
Test script to verify forecast error alerts
This simulates a forecast with >5% error to test the notification system
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from utils.telegram_notifier import TelegramNotifier
from Models.scheduler import evaluate_forecast_and_notify

def test_forecast_alert(actual=100, predicted=None, error_pct=None, model="ARIMA"):
    """
    Test the forecast alert system by simulating an error condition
    
    Args:
        actual (float): Simulated actual load value
        predicted (float): Simulated predicted load value
        error_pct (float): Direct error percentage to simulate (overrides actual/predicted)
        model (str): Model name to use in the alert
    """
    # Load environment variables
    load_dotenv()
    
    # Validate environment variables
    if not os.environ.get('TELEGRAM_BOT_TOKEN') or not os.environ.get('TELEGRAM_CHAT_ID'):
        print("Error: Missing Telegram credentials.")
        print("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env file.")
        return False
    
    # Calculate predicted if we're given an error percentage directly
    if error_pct is not None and predicted is None:
        # Convert error to a prediction that would generate this error
        # For a positive error (forecast too high)
        predicted = actual * (1 + error_pct/100)
    
    # If predicted still isn't set, use a default that generates >5% error
    if predicted is None:
        predicted = actual * 1.08  # 8% error
    
    print(f"Testing with actual={actual}, predicted={predicted}")
    
    # Call the evaluation function from scheduler.py
    try:
        error = evaluate_forecast_and_notify(actual, predicted, model)
        print(f"Test completed. Calculated error: {error:.2f}%")
        print("Check your Telegram for notifications if error > 5%")
        return True
    except Exception as e:
        print(f"Error during test: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the forecast error alert system")
    parser.add_argument("--actual", type=float, default=100.0, help="Actual load value")
    parser.add_argument("--predicted", type=float, help="Predicted load value")
    parser.add_argument("--error", type=float, help="Direct error percentage to simulate")
    parser.add_argument("--model", type=str, default="ARIMA", help="Model name for the alert")
    
    args = parser.parse_args()
    
    test_forecast_alert(
        actual=args.actual,
        predicted=args.predicted,
        error_pct=args.error,
        model=args.model
    )