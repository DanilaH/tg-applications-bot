# Deployment Guide

This guide describes how to deploy the Telegram Booking Bot to a Linux VPS (Virtual Private Server).

## MVP Deployment (Polling)

For a portfolio project or low-traffic bot, running via Long Polling is the simplest method as it doesn't require a domain name or SSL certificate.

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.12+
sudo apt install python3.12 python3.12-venv -y
```

### 2. Project Setup

```bash
# Clone the repo
git clone <your_repo_url> /opt/booking-bot
cd /opt/booking-bot

# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in `/opt/booking-bot`:

```bash
BOT_TOKEN=123456789:ABCDefgh...
ADMIN_CHAT_ID=987654321
DATABASE_URL=sqlite:///data/bookings.sqlite3
```

Make sure the `data` directory exists:
```bash
mkdir -p data
```

### 4. Running with systemd

To ensure the bot starts automatically on boot and restarts if it crashes, use a systemd service.

Create `/etc/systemd/system/booking-bot.service`:

```ini
[Unit]
Description=Telegram Booking Bot
After=network.target

[Service]
Type=simple
User=booking-bot
WorkingDirectory=/opt/booking-bot
ExecStart=/opt/booking-bot/.venv/bin/python -m bot.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Manage the service:**

```bash
# Start and enable
sudo systemctl daemon-reload
sudo systemctl enable booking-bot
sudo systemctl start booking-bot

# Check status
sudo systemctl status booking-bot

# View logs
journalctl -u booking-bot -f
```

> [!NOTE]
> For security, the bot runs under a dedicated `booking-bot` user. Ensure the directory belongs to them: `sudo chown -R booking-bot:booking-bot /opt/booking-bot`.

---

## Docker Deployment (Recommended for Portfolio/Demo)

If you prefer containerization, you can run the bot using Docker and Docker Compose.

### 1. Prerequisites
Ensure you have Docker and Docker Compose installed on your system.

### 2. Prepare Environment

**Linux / macOS:**
```bash
# Clone the repo
git clone <your_repo_url> /opt/booking-bot
cd /opt/booking-bot

# Create data directory for SQLite database
mkdir -p data

# Copy environment template
cp .env.example .env
# Edit .env with your favorite editor (e.g., nano)
nano .env
```

**Windows (PowerShell):**
```powershell
# Clone the repo
git clone <your_repo_url> C:\booking-bot
cd C:\booking-bot

# Create data directory for SQLite database
New-Item -ItemType Directory -Force -Path "data"

# Copy environment template
Copy-Item .env.example -Destination .env
# Edit .env with your favorite editor
notepad .env
```

> [!NOTE]
> The `.env` file is used to securely pass configuration to the container via the `env_file` directive in `docker-compose.yml`.
> The `./data` directory is mounted to `/app/data` inside the container as a volume to ensure the SQLite database (`bookings.sqlite3`) persists across container restarts and rebuilds.

### 3. Run the Bot

Start the container in detached mode:

```bash
docker compose up -d --build
```

### 4. Check Logs

To view the bot logs:

```bash
docker compose logs -f
```

---

## Maintenance

### Updating the Code
```bash
cd /opt/booking-bot
git pull
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart booking-bot
```

### Backups
The database is a single file: `/opt/booking-bot/data/bookings.sqlite3`. Periodically copy this file to a safe location.
