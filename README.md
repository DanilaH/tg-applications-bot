# Telegram booking bot

Portfolio demo of a Telegram bot that collects booking requests for a local
business. The bot currently supports the `/start` command and displays the main
menu with a booking button. The booking flow will be added in later features.

## Stack

- Python 3.12+
- aiogram 3.x
- pydantic-settings
- pytest
- Ruff

## Local setup on Windows

Run the following commands in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Fill in `.env` with values created for local development:

```text
BOT_TOKEN=your_bot_token
ADMIN_CHAT_ID=your_admin_chat_id
```

Never commit `.env` or real Telegram credentials.

## Run

With the virtual environment active:

```powershell
python -m bot.main
```

Send `/start` to the bot to see the welcome message and the main menu. The
booking button will become active when service selection is added in the next
feature. Stop polling with `Ctrl+C`.

## Checks

```powershell
python -m ruff check .
python -m pytest
```

Automated tests do not connect to Telegram or send messages.
