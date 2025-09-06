# Environment Setup Guide

This guide explains how to properly set up environment variables for the Electric Load Forecasting project.

## Setting Up Your Environment

### Automatic Setup (Recommended)

1. Run the setup script:
   ```bash
   python setup_env.py
   ```

2. Follow the prompts to configure your environment variables.

### Manual Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Open the `.env` file in a text editor.

3. Fill in your specific values for each variable.

## Required Environment Variables

### Telegram Notification Setup

To enable Telegram notifications for forecast errors:

1. **Create a Telegram Bot**:
   - Start a chat with [@BotFather](https://t.me/BotFather) on Telegram
   - Send `/newbot` command and follow instructions
   - Save the API token provided

2. **Get Your Chat ID**:
   - Start a conversation with [@userinfobot](https://t.me/userinfobot)
   - It will respond with your chat ID

3. **Add to Environment Variables**:
   ```
   TELEGRAM_BOT_TOKEN="your_bot_token"
   TELEGRAM_CHAT_ID="your_chat_id"
   ```

## Security Best Practices

1. **Never commit `.env` files to version control**
   - Our `.gitignore` is configured to prevent this
   - Check before committing: `git status`

2. **Use different environment files for different environments**
   - Development: `.env.development`
   - Production: `.env.production`

3. **Set restrictive file permissions**
   - On Linux/Mac: `chmod 600 .env`
   - This restricts read/write access to the file owner only

4. **Use strong, unique passwords and API keys**
   - Generate strong passwords with: `python -c "import secrets; print(secrets.token_urlsafe(20))"`

5. **Rotate secrets regularly**
   - Update API keys and passwords periodically
   - Update all environment files when rotating secrets

## Environment Variables in the Codebase

Our codebase loads environment variables in these key files:

1. **Django Settings** (`website/settings.py`):
   - Uses `os.environ.get()` with fallbacks for critical settings

2. **Telegram Notifications** (`utils/telegram_notifier.py`):
   - Uses `dotenv.load_dotenv()` to load environment variables
   - Accesses variables via `os.environ.get()`

3. **Scripts and Models**:
   - All scripts needing environment variables should import and call `load_dotenv()`

## Testing Your Environment Setup

1. Verify Telegram notifications:
   ```bash
   python test_telegram.py
   ```

2. Test forecast error alerts:
   ```bash
   python test_forecast_alert.py --error 8.5
   ```

If you receive the test notifications in your Telegram, your environment is correctly set up!