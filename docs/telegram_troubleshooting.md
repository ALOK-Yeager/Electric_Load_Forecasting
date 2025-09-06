# Telegram Integration Troubleshooting Guide

If you're experiencing issues with Telegram notifications in the Electric Load Forecasting system, this guide will help you troubleshoot and resolve common problems.

## Common Error: 404 Not Found

If you see an error like this:
```
Failed to send Telegram message: 404 Client Error: Not Found for url: https://api.telegram.org/bot[TOKEN]/sendMessage
```

This typically means one of the following:

1. **Duplicated or malformed bot token**
2. **Invalid bot token**
3. **Network connectivity issues**

## Quick Fix: Run the Token Fix Tool

We've created a tool to automatically detect and fix common token issues:

```bash
python fix_token.py
```

This will:
1. Check your token format
2. Fix common issues like duplication
3. Test the connection to Telegram API

## Step-by-Step Troubleshooting

If the automatic tool doesn't resolve your issue, follow these steps:

### 1. Verify Your Bot Token

A valid Telegram bot token looks like this: `123456789:ABCDEfghIJKLmnopQRSTUvwxyz`

- It contains one colon (`:`) separating numbers and letters
- It shouldn't be duplicated or contain extra characters

**How to fix:**
- Get a new token from [@BotFather](https://t.me/BotFather) if needed
- Update your `.env` file with the correct token:
  ```
  TELEGRAM_BOT_TOKEN="your_correct_token"
  ```

### 2. Check Chat ID Format

Your chat ID should be a number (for personal chats) or start with `-` for group chats.

**How to fix:**
- Get your correct chat ID by sending a message to [@userinfobot](https://t.me/userinfobot)
- Update your `.env` file with the correct chat ID

### 3. Verify Bot Permissions

Your bot needs permission to send messages to you.

**How to fix:**
1. Start a conversation with your bot by sending it a message first
2. For group chats, add the bot to the group and give it permission to send messages

### 4. Check Environment Variables

Make sure the environment variables are being loaded correctly:

```python
from dotenv import load_dotenv
import os

load_dotenv()
token = os.environ.get('TELEGRAM_BOT_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

print(f"Token: {token[:4]}...{token[-4:] if token else 'None'}")
print(f"Chat ID: {chat_id}")
```

### 5. Manually Test the API

You can test the Telegram API directly with this command:

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage" -d "chat_id=<YOUR_CHAT_ID>&text=Test"
```

Replace `<YOUR_BOT_TOKEN>` and `<YOUR_CHAT_ID>` with your values.

## Common Solutions

### Solution for Duplicated Token

If your token appears twice in the URL like:
```
https://api.telegram.org/botTOKEN_HERTOKEN_HERE/sendMessage
```

Fix by editing your `.env` file to contain only one clean token:
```
TELEGRAM_BOT_TOKEN="correct_single_token_here"
```

### Solution for Network Issues

If your network blocks Telegram API:

1. Check if you need a proxy to access Telegram
2. Verify that outbound connections to `api.telegram.org` are allowed

## Getting Additional Help

If you're still experiencing issues:

1. Run the diagnostic tool with debug logging:
   ```bash
   python -m logging -v DEBUG test_telegram.py
   ```

2. Check the full error response:
   ```bash
   PYTHONVERBOSE=2 python test_telegram.py
   ```

3. Review the Telegram Bot API documentation:
   [https://core.telegram.org/bots/api](https://core.telegram.org/bots/api)