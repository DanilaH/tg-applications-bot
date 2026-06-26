# Telegram Booking Bot

A portfolio demo of a Telegram bot designed to automate booking collection for local businesses (e.g., barbershops, beauty salons, or consulting services).

## Business Goal

The project aims to provide a lightweight, reliable way for small businesses to receive and manage client bookings without expensive CRM systems. It automates the data collection process, ensures all required information is gathered, and immediately notifies the business owner via Telegram.

## Key Features

- **Automated Booking Flow**: A guided multi-step process to collect service type, client name, phone number, and optional comments.
- **Admin Notifications**: Instant alerts for new bookings sent directly to the administrator's Telegram.
- **Interactive Admin Actions**: Admins can "Accept" or "Decline" bookings directly from the notification message, updating the status in the database.
- **Persistent Storage**: All bookings are stored in a local SQLite database with their current status (`new`, `accepted`, `declined`).
- **Robust Input Validation**: Validates name length, phone formats (text or Telegram contact), and comment lengths.
- **State Management**: Uses FSM (Finite State Machine) to handle complex user interactions.

## How It Works

### User Flow
1. User sends `/start` and clicks **"Записаться"** (Book Now).
2. **Service Selection**: Inline buttons for available services (e.g., Haircut, Consultation).
3. **Name Entry**: Text input (2–80 characters).
4. **Phone Entry**: User can type their number or use the "Send Phone Number" button.
5. **Optional Comment**: User can add a note or skip this step.
6. **Summary & Confirmation**: User reviews their data and confirms the request.
7. **Success**: Data is saved, and a notification is sent to the admin.

### Admin Flow
1. Admin receives a message with all booking details.
2. Admin clicks **"Принять"** (Accept) or **"Отклонить"** (Decline).
3. The bot updates the booking status in SQLite and confirms the action to the admin.

## Local Setup (Windows PowerShell)

Follow these steps to run the bot locally:

```powershell
# Clone the repository and enter the directory
# git clone <repo_url>
# cd telegram-booking-bot

# Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r requirements-dev.txt

# Create .env file from example
Copy-Item .env.example .env
```

### Configuration

Open the `.env` file and fill in your credentials:

```text
BOT_TOKEN=your_bot_token
ADMIN_CHAT_ID=your_admin_chat_id
DATABASE_URL=sqlite:///data/bookings.sqlite3
```

> [!IMPORTANT]
> **Security Warning**: Never commit your `.env` file or any real Telegram tokens to version control. The `.gitignore` is configured to exclude `.env` and SQLite database files.

## Running the Bot

With the virtual environment active:

```powershell
python -m bot.main
```

Send `/start` to your bot in Telegram to begin. Press `Ctrl+C` in the terminal to stop.

## Project Verification

To ensure code quality and run tests:

```powershell
# Linting
python -m ruff check .

# Unit Tests
python -m pytest

# Dependency Check
python -m pip check
```

## Tech Stack

- **Python 3.12+**
- **aiogram 3.x**: Modern asynchronous framework for Telegram Bots.
- **Pydantic Settings**: Configuration management via environment variables.
- **SQLite**: Lightweight relational database.
- **Pytest**: For automated testing.
- **Ruff**: Fast Python linter.
