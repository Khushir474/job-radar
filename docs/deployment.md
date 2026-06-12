# Deployment Guide

This guide covers deploying Job Radar for 24/7 operation.

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [VPS Deployment (Recommended)](#vps-deployment-recommended)
4. [Cloud Platform Deployment](#cloud-platform-deployment)
5. [Hermes Cron Integration](#hermes-cron-integration)
6. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Local Development

### Prerequisites
- Python 3.11+
- macOS (for iMessage) or Linux
- Git

### Setup
```bash
# Clone and enter directory
cd job-radar

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Copy config template
cp config/config.yaml.example config/config.yaml
cp .env.example .env

# Edit configuration
# - Add your alert credentials to .env
# - Add custom companies to config/user_companies.yaml

# Initialize database
job-radar init-db

# Test
job-radar check
job-radar test-alerts
```

---

## Docker Deployment

### Quick Start
```bash
# Build and run
docker-compose up -d --build job-radar-cron

# View logs
docker-compose logs -f job-radar-cron

# Stop
docker-compose down
```

### Manual Run (One-off)
```bash
docker-compose run --rm job-radar-test
```

### With External Database
```yaml
# docker-compose.override.yml
services:
  job-radar-cron:
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/jobradar
    depends_on:
      - db

  db:
    image: postgres:16
    environment:
      - POSTGRES_DB=jobradar
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

---

## VPS Deployment (Recommended)

### Recommended Providers
| Provider | Plan | Cost/mo | Specs |
|----------|------|---------|-------|
| **Hetzner** | CX22 | €4.51 | 2 vCPU, 4GB RAM, 40GB SSD |
| **DigitalOcean** | Basic | $6 | 1 vCPU, 1GB RAM, 25GB SSD |
| **Linode** | Nanode | $5 | 1 vCPU, 1GB RAM, 25GB SSD |
| **Vultr** | Cloud Compute | $6 | 1 vCPU, 1GB RAM, 25GB SSD |

### Server Setup (Ubuntu 22.04/24.04)

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# 3. Install Docker Compose
sudo apt install docker-compose-plugin

# 4. Create app directory
mkdir -p ~/job-radar && cd ~/job-radar

# 5. Clone repository
git clone https://github.com/Khushir474/job-radar.git .

# 6. Configure environment
cp .env.example .env
# Edit .env with your credentials
nano .env

# 7. Configure companies (optional)
cp config/user_companies.yaml.example config/user_companies.yaml
nano config/user_companies.yaml

# 8. Build and start
docker compose up -d --build job-radar-cron

# 9. Check logs
docker compose logs -f job-radar-cron
```

### Systemd Service (Alternative to Docker)

Create `/etc/systemd/system/job-radar.service`:

```ini
[Unit]
Description=Job Radar - AI Job Alert System
After=network.target

[Service]
Type=simple
User=jobradar
WorkingDirectory=/home/jobradar/job-radar
Environment=PATH=/home/jobradar/job-radar/.venv/bin
EnvironmentFile=/home/jobradar/job-radar/.env
ExecStart=/home/jobradar/job-radar/.venv/bin/python -m job_radar.cli check
Restart=always
RestartSec=7200  # 2 hours

# Run every 2 hours via systemd timer instead
```

Create `/etc/systemd/system/job-radar.timer`:

```ini
[Unit]
Description=Run Job Radar every 2 hours

[Timer]
OnCalendar=*:0/2
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now job-radar.timer
```

---

## Cloud Platform Deployment

### Railway.app (Easiest - $5/mo)
```bash
# 1. Install Railway CLI
npm i -g @railway/cli

# 2. Login and link
railway login
railway init

# 3. Set environment variables
railway variables set TELEGRAM_BOT_TOKEN=xxx
railway variables set TELEGRAM_CHAT_IDS=xxx
# ... add all variables

# 4. Deploy
railway up

# 5. Add cron job in Railway dashboard (Settings > Cron Jobs)
# Schedule: "0 */2 * * *" (every 2 hours)
# Command: "python -m job_radar.cli check"
```

### Fly.io (Docker-native - ~$5/mo)
```bash
# 1. Install flyctl
curl -L https://fly.io/install.sh | sh

# 2. Launch
fly launch --name job-radar

# 3. Set secrets
fly secrets set TELEGRAM_BOT_TOKEN=xxx
fly secrets set TELEGRAM_CHAT_IDS=xxx
# ...

# 4. Deploy
fly deploy

# 5. Add cron via fly.toml
# [processes]
# cron = "python -m job_radar.cli check"
# 
# [services.cron]
# schedule = "0 */2 * * *"
```

### Modal.com (Serverless - Pay per use)
```python
# modal_app.py
import modal

app = modal.App("job-radar")

image = modal.Image.debian_slim().pip_install_from_pyproject("pyproject.toml")

@app.function(
    image=image,
    schedule=modal.Cron("0 */2 * * *"),  # Every 2 hours
    secrets=[
        modal.Secret.from_name("job-radar-secrets"),
    ],
    volumes={"/data": modal.Volume.from_name("job-radar-data", create_if_missing=True)},
)
async def check_jobs():
    import sys
    sys.path.insert(0, "/app/src")
    from job_radar.scripts.check_jobs import check_jobs
    await check_jobs()
```

Deploy:
```bash
modal deploy modal_app.py
```

### GitHub Actions (Free - Limited)
```yaml
# .github/workflows/check-jobs.yml
name: Check Jobs

on:
  schedule:
    - cron: '0 */2 * * *'  # Every 2 hours
  workflow_dispatch:

jobs:
  check:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
          
      - name: Run job check
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_IDS: ${{ secrets.TELEGRAM_CHAT_IDS }}
          DISCORD_WEBHOOK_URL: ${{ secrets.DISCORD_WEBHOOK_URL }}
          # ... other secrets
        run: python -m job_radar.cli check
```

---

## Hermes Cron Integration

Since you're using Hermes, you can also run the check via Hermes cron jobs:

### Create Cron Job
```bash
# Create cron job that runs every 2 hours
hermes cron create "every 2h" \
  --prompt "Run job-radar check: python -m job_radar.cli check" \
  --skills "terminal" \
  --deliver origin

# Or with quiet hours (Hermes doesn't have built-in quiet hours,
# so the script handles it internally)
```

### Using Hermes Cron with Script
The script already handles quiet hours internally, so you can just schedule it to run every 2 hours and it will skip execution during quiet hours.

---

## Monitoring & Maintenance

### Health Checks
```bash
# Check if service is running
docker compose ps

# View recent logs
docker compose logs --tail=100 job-radar-cron

# Check database
sqlite3 data/job_radar.db "SELECT COUNT(*) FROM jobs;"

# Check alerts log
tail -20 data/alerts.log
```

### Log Rotation
Add to `/etc/logrotate.d/job-radar`:
```
/home/jobradar/job-radar/logs/*.log {
    daily
    rotate 30
    compress
    missingok
    notifempty
}
```

### Database Maintenance
```bash
# Vacuum database monthly (run via cron)
sqlite3 data/job_radar.db "VACUUM;"

# Clean old seen jobs (older than 90 days)
sqlite3 data/job_radar.db "DELETE FROM seen_jobs WHERE first_seen < date('now', '-90 days');"
```

### Updating
```bash
# Pull latest changes
cd ~/job-radar && git pull

# Rebuild and restart
docker compose up -d --build job-radar-cron
```

---

## Troubleshooting

### No alerts received
1. Check alert channel configuration: `job-radar test-alerts`
2. Verify credentials in `.env`
3. Check logs: `docker compose logs job-radar-cron`

### Jobs not found
1. Run manual check: `job-radar check`
2. Check scraper status in logs
3. Some sites may have changed - update scrapers

### Database locked
1. Ensure only one instance is running
2. Check for zombie processes: `ps aux | grep job_radar`

### Rate limited
1. Increase `request_timeout` and `retry_delay` in config
2. Reduce `max_concurrent_scrapers`

---

## Security Notes

- Never commit `.env` or `config/config.yaml` with real credentials
- Use strong, unique passwords for SMTP
- Rotate Telegram bot tokens periodically
- Use app-specific passwords for Gmail SMTP
- Keep Docker images updated: `docker compose pull && docker compose up -d --build`