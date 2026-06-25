# Telegram booking bot

Portfolio demo of a Telegram bot that collects booking requests for a local
business. The bot supports a multi-step booking flow: service selection → name →
phone → comment → summary, admin notification, and SQLite storage.

## Current flow

```
/start
→ кнопка "Записаться"
→ inline-кнопки: выбор услуги
→ ввод имени (текст, 2–80 символов)
→ ввод телефона (текст или Telegram contact, кнопка «Отмена»)
→ комментарий (текст до 500 символов, кнопка «Пропустить», «Отмена»)
→ проверка итоговой заявки
→ подтверждение, повторное заполнение или отмена
→ сохранение заявки в SQLite
→ отправка заявки администратору
```

После подтверждения заявка сохраняется в локальную SQLite-базу и отправляется
администратору в Telegram с кнопками «Принять» и «Отклонить». Если отправка в
Telegram временно не удалась, заявка не дублируется при повторной попытке.

Администратор может изменить статус заявки в базе данных прямо из Telegram.
Статус (`new`, `accepted` или `declined`) хранится в SQLite.

Услуги для demo:

- `men_haircut` — Мужская стрижка
- `beard_trim` — Борода и контур
- `combo` — Стрижка + борода
- `consultation` — Консультация

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
DATABASE_URL=sqlite:///data/bookings.sqlite3
```

Never commit `.env` or real Telegram credentials.

## Stored data

SQLite stores demo booking requests in `data/bookings.sqlite3` by default. The
app saves service, customer name, phone, optional comment, Telegram user id,
optional username, status `new`, and UTC creation time. The `data/` directory and
local database files are ignored by git.

## Run

With the virtual environment active:

```powershell
python -m bot.main
```

Send `/start` to the bot to see the welcome message and the main menu.
Stop polling with `Ctrl+C`.

## Checks

```powershell
python -m ruff check .
python -m pytest
```

Automated tests do not connect to Telegram or send messages.
