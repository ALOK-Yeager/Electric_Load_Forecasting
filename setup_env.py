#!/usr/bin/env python3
"""
Environment Setup Script for Electric Load Forecasting Project

This script helps generate a proper .env file from .env.example,
prompting for necessary values while maintaining security best practices.
"""

import os
import sys
import secrets
import getpass
from pathlib import Path
import shutil

def generate_secret_key():
    """Generate a secure random secret key for Django"""
    return secrets.token_urlsafe(50)

def get_user_input(prompt, default=None, password=False):
    """Get input from user with support for defaults and password masking"""
    if default:
        prompt = f"{prompt} [default: {default}]: "
    else:
        prompt = f"{prompt}: "
    
    if password:
        value = getpass.getpass(prompt)
    else:
        value = input(prompt)
    
    return value if value else default

def setup_env_file():
    """Set up the .env file based on .env.example"""
    
    # Check if .env.example exists
    example_file = Path(".env.example")
    if not example_file.exists():
        print("Error: .env.example file not found.")
        return False
    
    # Check if .env already exists
    env_file = Path(".env")
    if env_file.exists():
        overwrite = get_user_input("A .env file already exists. Overwrite? (yes/no)", default="no")
        if overwrite.lower() not in ["yes", "y"]:
            print("Setup cancelled. Existing .env file preserved.")
            return False
    
    # Copy example file as a starting point
    shutil.copy(example_file, env_file)
    
    print("\n===== Electric Load Forecasting Environment Setup =====")
    print("Let's set up your environment variables for development or production.\n")
    
    # Environment type
    env_type = get_user_input(
        "Select environment (development/production)", 
        default="development"
    )
    
    # Generate and replace variables in the .env file
    with open(env_file, "r") as file:
        env_content = file.read()
    
    # Replace environment-specific values
    replacements = {
        'ENVIRONMENT="development"': f'ENVIRONMENT="{env_type}"',
        'DEBUG="True"': f'DEBUG="{"True" if env_type == "development" else "False"}"',
        'SECRET_KEY="django-insecure-change-this-in-production"': f'SECRET_KEY="{generate_secret_key()}"'
    }
    
    for old, new in replacements.items():
        env_content = env_content.replace(old, new)
    
    # Get Telegram credentials
    print("\n----- Telegram Notification Setup -----")
    print("To set up Telegram notifications, you need a bot token and chat ID.")
    print("Instructions:")
    print("1. Create a bot via @BotFather on Telegram")
    print("2. Get your chat ID by sending a message to @userinfobot\n")
    
    telegram_token = get_user_input("Enter your Telegram bot token", password=True)
    telegram_chat_id = get_user_input("Enter your Telegram chat ID")
    
    if telegram_token:
        env_content = env_content.replace('TELEGRAM_BOT_TOKEN="your_bot_token_here"', f'TELEGRAM_BOT_TOKEN="{telegram_token}"')
    
    if telegram_chat_id:
        env_content = env_content.replace('TELEGRAM_CHAT_ID="your_chat_id_here"', f'TELEGRAM_CHAT_ID="{telegram_chat_id}"')
    
    # Database setup if production
    if env_type == "production":
        print("\n----- Database Setup -----")
        db_password = get_user_input("Enter database password", password=True)
        db_host = get_user_input("Enter database host", default="localhost")
        
        if db_password:
            env_content = env_content.replace('DB_PASSWORD="db_password"', f'DB_PASSWORD="{db_password}"')
        
        if db_host:
            env_content = env_content.replace('DB_HOST="localhost"', f'DB_HOST="{db_host}"')
    
    # Write the updated content back
    with open(env_file, "w") as file:
        file.write(env_content)
    
    # Set appropriate permissions for .env file (Linux/Mac)
    try:
        if sys.platform != "win32":
            os.chmod(env_file, 0o600)  # Read/write for owner only
    except Exception as e:
        print(f"Warning: Could not set permissions on .env file: {str(e)}")
    
    print("\n✅ Environment file setup complete!")
    print(f"Your .env file has been created for {env_type} environment.")
    print("\nIMPORTANT SECURITY NOTES:")
    print("1. NEVER commit your .env file to version control")
    print("2. Keep your secret keys and passwords secure")
    print("3. For production, ensure the .env file has restricted permissions")
    
    return True

if __name__ == "__main__":
    # Ensure we're in the right directory
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)
    
    # Run the setup
    setup_env_file()