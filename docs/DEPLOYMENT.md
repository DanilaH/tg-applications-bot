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
User=root
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

---

## Future Scaling: Docker Plan

If you prefer containerization, here is the suggested approach:

### Dockerfile (Proposed)
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./bot/
CMD ["python", "-m", "bot.main"]
```

### docker-compose.yml (Proposed)
```yaml
services:
  bot:
    build: .
    restart: always
    env_file: .env
    volumes:
      - ./data:/app/data
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
