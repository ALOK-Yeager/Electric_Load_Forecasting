#!/usr/bin/env python3
"""
Telegram Token Fix Tool

This script checks for and fixes common issues with Telegram bot tokens
in environment variables or .env files.
"""

import os
import re
import sys
from dotenv import load_dotenv, find_dotenv, set_key

def validate_token(token):
    """
    Validate a Telegram bot token format and return a fixed version if needed.
    
    Args:
        token (str): The token to validate
        
    Returns:
        tuple: (is_valid, fixed_token)
    """
    if not token:
        return False, None
    
    # Remove any whitespace
    token = token.strip()
    
    # Check for basic format: numbers:letters
    if not ":" in token:
        print(f"❌ Token is missing the required format (numbers:alphanumeric)")
        return False, None
    
    # Check if token is duplicated
    if token.count(':') > 1:
        print(f"⚠️ Token appears to be duplicated in the format")
        
        # Extract the first valid token pattern
        match = re.search(r'(\d+):([A-Za-z0-9_-]+)', token)
        if match:
            fixed_token = f"{match.group(1)}:{match.group(2)}"
            print(f"✅ Fixed token format")
            return True, fixed_token
    
    # Check if token matches the expected pattern
    match = re.search(r'(\d+):([A-Za-z0-9_-]+)', token)
    if not match:
        print(f"❌ Token doesn't match expected pattern (numbers:alphanumeric)")
        return False, None
    
    return True, token

def fix_env_token():
    """
    Check and fix the Telegram token in the .env file
    
    Returns:
        bool: True if fixed or valid, False if failed
    """
    # Load environment variables
    env_file = find_dotenv(usecwd=True)
    if not env_file:
        print("❌ No .env file found. Create one first.")
        return False
    
    # Load the file
    load_dotenv(env_file)
    
    # Get the token
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token:
        print("❌ No TELEGRAM_BOT_TOKEN found in environment variables.")
        return False
    
    # Validate and get fixed token if needed
    is_valid, fixed_token = validate_token(token)
    
    # If already valid, no need to update
    if is_valid and fixed_token == token:
        print("✅ Telegram token is valid.")
        return True
    
    # If not valid and couldn't be fixed
    if not is_valid and not fixed_token:
        print("\n❌ Could not fix the token format. Please manually update your token.")
        print("A valid Telegram bot token typically looks like: 123456789:ABCDEFGhijklmnopQRSTUVwxyz")
        return False
    
    # Update the token in the .env file
    print(f"🔄 Updating token in {env_file}")
    set_key(env_file, 'TELEGRAM_BOT_TOKEN', fixed_token)
    
    print("✅ Token updated successfully. Please try your command again.")
    return True

def test_token_request():
    """Test a direct request to the Telegram API with the token"""
    import requests
    
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token:
        print("❌ No token found in environment variables")
        return False
    
    # Test token by making a getMe request
    try:
        print(f"🔄 Testing token with Telegram API...")
        response = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get('ok'):
                bot_name = bot_info['result'].get('username')
                print(f"✅ Token is valid! Connected to bot: @{bot_name}")
                return True
            else:
                print(f"❌ Token was rejected by Telegram: {bot_info.get('description')}")
        else:
            print(f"❌ Request failed with status code {response.status_code}")
            print(f"Error: {response.text}")
    
    except Exception as e:
        print(f"❌ Error testing token: {str(e)}")
    
    return False

if __name__ == "__main__":
    print("🔧 Telegram Token Fix Tool")
    print("=========================")
    
    # Try to fix the token
    fixed = fix_env_token()
    
    if fixed:
        # If fixed, test it
        print("\n🔍 Testing the token with Telegram API")
        test_token_request()
    
    print("\n📋 Next steps:")
    print("1. Make sure your bot token is correct")
    print("2. Ensure you've started a conversation with your bot")
    print("3. Run 'python test_telegram.py' to test again")