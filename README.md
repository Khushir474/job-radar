# Job Radar 🔍

Automated job alert system for **Data Analyst, Data Scientist, ML Engineer, and AI roles** at **30+ top AI companies** plus your custom companies. Sends alerts via **iMessage, Telegram, Discord, Email, and File** every 30 minutes with quiet hours (10 PM - 6 AM PST).

## Features

- 🎯 **30+ Built-in AI Companies**: OpenAI, Anthropic, DeepMind, Meta AI, NVIDIA, Hugging Face, Cohere, Mistral, and more
- ➕ **Custom Companies**: Add your own companies via CLI or config file
- 🔍 **Smart Filtering**: Role-based keywords, location preferences, experience levels
- 📱 **Multi-Channel Alerts**: iMessage, Telegram, Discord, Email, File (JSON/Markdown)
- ⏰ **Quiet Hours**: Automatic pause 10 PM - 6 AM PST (configurable)
- 🐳 **Docker Ready**: Containerized for easy deployment
- ☁️ **Cloud Deployable**: Railway, Fly.io, Modal, VPS, GitHub Actions
- 📊 **Deduplication**: Never get duplicate alerts for the same job
- 📈 **Tracking**: SQLite database with full job history

## Quick Start

### Local Development
```bash
# Clone
git clone https://github.com/Khushir474/job-radar.git
cd job-radar

# Setup
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Configure
cp config/config.yaml.example config/config.yaml
cp .env.example .env
# Edit .env with your alert credentials

# Initialize
job-radar init-db

# Test
job-radar check
job-radar test-alerts
```

### Docker (Recommended for 24/7)
```bash
# Configure
cp .env.example .env
# Edit .env with your credentials

# Build and run
docker-compose up -d --build job-radar-cron

# View logs
docker-compose logs -f job-radar-cron
```

## Built-in Companies (30+)

| Company | ATS | Priority |
|---------|-----|----------|
| OpenAI | Greenhouse | 1 |
| Anthropic | Greenhouse | 1 |
| Google DeepMind | Custom | 1 |
| Meta AI | Custom | 1 |
| Microsoft Research | Custom | 1 |
| NVIDIA | Workday | 1 |
| Apple ML | Custom | 1 |
| Amazon Science | Custom | 1 |
| Tesla AI | Custom | 1 |
| Adobe Research | Custom | 2 |
| Hugging Face | Greenhouse | 1 |
| Cohere | Greenhouse | 1 |
| Mistral AI | Greenhouse | 1 |
| Perplexity | Greenhouse | 1 |
| Databricks | Workday | 1 |
| Palantir | Custom | 1 |
| Scale AI | Greenhouse | 1 |
| Weights & Biases | Greenhouse | 2 |
| LangChain | Greenhouse | 1 |
| Runway | Greenhouse | 1 |
| Stability AI | Greenhouse | 1 |
| Midjourney | Custom | 2 |
| ElevenLabs | Greenhouse | 1 |
| Replicate | Greenhouse | 1 |
| Modal | Greenhouse | 1 |
| Together AI | Greenhouse | 1 |
| Fireworks AI | Greenhouse | 1 |
| Anyscale | Greenhouse | 1 |
| MosaicML | Greenhouse | 2 |
| Adept | Greenhouse | 2 |
| Character.AI | Greenhouse | 1 |
| Inflection AI | Greenhouse | 2 |

## Alert Channels

### Telegram (Recommended)
1. Create bot with [@BotFather](https://t.me/BotFather)
2. Get chat ID: `curl "https://api.telegram.org/bot<TOKEN>/getUpdates"`
3. Add to `.env`:
   ```
   TELEGRAM_BOT_TOKEN=your_token
   TELEGRAM_CHAT_IDS=-1001234567890,123456789
   ```

### Discord
1. Create webhook in Server Settings → Integrations → Webhooks
2. Add to `.env`:
   ```
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
   ```

### Email (SMTP)
```
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_FROM="Job Radar <your@gmail.com>"
EMAIL_RECIPIENTS=you@example.com,team@example.com
```

### iMessage (macOS only)
```bash
# Install imsg CLI
brew install imessage-mcp

# Or use built-in AppleScript (no extra install)
IMESSAGE_RECIPIENTS="+15551234567,user@icloud.com"
```

### File (Always Enabled)
Logs all alerts to `data/alerts.log` in JSON format for review.

## Configuration

### Quiet Hours
Default: **10 PM - 6 AM PST** (configurable)
```yaml
scheduler:
  quiet_hours_start: "22:00"
  quiet_hours_end: "06:00"
  timezone: "America/Los_Angeles"
```

### Role Filters
Track specific roles:
```yaml
filters:
  roles:
    - "data_analyst"
    - "data_scientist"
    - "ml_engineer"
    - "ai_engineer"
    - "research_scientist"
```

### Location Filters
```yaml
filters:
  locations:
    - "Remote"
    - "San Francisco"
    - "New York"
    - "Seattle"
```

## Adding Custom Companies

### Via CLI
```bash
job-radar companies --add
# Enter: ID, Name, Career URL, ATS Type, Config
```

### Via Config File
Edit `config/user_companies.yaml`:
```yaml
companies:
  - id: "my-startup"
    name: "My AI Startup"
    career_url: "https://myaistartup.com/careers"
    ats_type: "greenhouse"
    ats_config:
      board_token: "myaistartup"
    search_keywords: ["ml", "ai", "llm"]
    enabled: true
    priority: 5
```

## Deployment Options (24/7)

| Platform | Cost | Effort | Best For |
|----------|------|--------|----------|
| **Fly.io** ⭐ | $5-10/mo | Low | **Production-grade, Docker-native, resume builder** |
| **Railway.app** | $5/mo | Very Low | Teams, easiest UI, no Docker knowledge |
| **VPS (Hetzner)** | €4.51/mo | Medium | Cheapest, full control, manual setup |
| **Modal.com** | Pay-per-use | Low | Serverless, scales to zero |

**Recommended:** Fly.io for production deployments and resume impact (see [Fly.io section](#flyio-production-deployment-) below)

### VPS Setup (Hetzner CX22 - €4.51/mo)
```bash
# On server
curl -fsSL https://get.docker.com | sh
git clone https://github.com/Khushir474/job-radar.git
cd job-radar
cp .env.example .env  # Add credentials
docker compose up -d --build job-radar-cron
```

### Fly.io (Production Deployment) ⭐

**Best for:** Production-grade deployment, Docker expertise, resume builder, global reach.

#### Prerequisites
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Sign up (free account)
fly auth signup
# or
fly auth login
```

#### Setup (10 minutes)

**1. Initialize Fly.io**
```bash
cd job-radar
fly launch --name job-radar
```
Follow prompts:
- Region: Choose closest to you (sjc = San Jose, lax = LA, ord = Chicago, etc.)
- PostgreSQL: No (use persistent volumes instead)
- Accept `fly.toml` configuration

**2. Create Persistent Volumes** (for data storage)
```bash
fly volumes create job_radar_data --size 1
fly volumes create job_radar_logs --size 1
```

**3. Set Secrets** (environment variables)
```bash
fly secrets set TELEGRAM_BOT_TOKEN=your_bot_token
fly secrets set TELEGRAM_CHAT_IDS=123456789,-1001234567890
fly secrets set DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
fly secrets set EMAIL_SMTP_HOST=smtp.gmail.com
fly secrets set EMAIL_SMTP_PORT=587
fly secrets set EMAIL_USERNAME=your@gmail.com
fly secrets set EMAIL_PASSWORD=your_app_password
fly secrets set EMAIL_FROM="Job Radar <your@gmail.com>"
fly secrets set EMAIL_RECIPIENTS=user1@example.com,user2@example.com
fly secrets set CHECK_INTERVAL_HOURS=2
fly secrets set QUIET_HOURS_START=22:00
fly secrets set QUIET_HOURS_END=06:00
fly secrets set TIMEZONE=America/Los_Angeles
fly secrets set LOG_LEVEL=INFO
```

**4. Deploy**
```bash
fly deploy
```

**5. Set Up Cron Job** (2-hour scheduling)
```bash
fly machine run \
  --name job-radar-cron \
  --schedule "0 */2 * * *" \
  python -m job_radar.cli check
```

**6. Test**
```bash
# Run check manually
fly ssh console -s
python -m job_radar.cli check
python -m job_radar.cli test-alerts
exit
```

#### Monitoring & Logs
```bash
# Real-time logs
fly logs

# Check status
fly status

# SSH into instance for debugging
fly ssh console

# View volumes
fly volumes list
```

#### Updating Code
```bash
git push origin main
fly deploy
# Live in ~2 minutes
```

#### Scaling & Performance
```bash
# View instances
fly machines list

# Increase memory if needed
fly machines update <machine-id> --memory 512

# Check current cost
fly billing summary
```

#### Cost Breakdown
- **Compute:** $5-10/mo (pay only for runtime)
- **Persistent Storage:** ~$0.15/GB/mo (1GB = $0.15/mo)
- **Total:** ~$5.50/mo typical

**Cheaper if you:**
- Stop cron job (manual trigger only)
- Scale down to shared CPU

#### Monitoring Dashboard
- Go to [fly.io/dashboard](https://fly.io/dashboard)
- View real-time metrics, logs, deployments
- One-click rollbacks

#### Production Checklist
- ✅ Docker containerization
- ✅ Environment secrets (not in code)
- ✅ Persistent data volumes
- ✅ Monitoring & logs
- ✅ Auto-rollback on failure
- ✅ Global CDN distribution
- ✅ Health checks

---

### Railway.app (Easiest for Beginners)

If you prefer a **no-SSH, web-UI-only** approach, see [docs/railway.md](docs/railway.md) (Railway is great for teams but simpler tech stack)

### Modal.com (Serverless)
```bash
pip install modal
modal deploy modal_app.py
# Runs every 2 hours automatically
```

## Hermes Cron Integration

If using Hermes Agent, create a cron job:
```bash
hermes cron create "every 2h" \
  --prompt "Run job-radar check: python -m job_radar.cli check" \
  --skills "terminal" \
  --deliver origin
```

The script handles quiet hours internally (skips during 10PM-6AM PST).

## Project Structure

```
job-radar/
├── src/job_radar/
│   ├── models/         # Pydantic models
│   ├── scrapers/       # ATS scrapers (Greenhouse, Lever, Workday, etc.)
│   ├── matcher/        # Job matching engine
│   ├── storage/        # Database operations
│   ├── alerts/         # Alert channels (Telegram, Discord, Email, iMessage, File)
│   ├── scheduler/      # Quiet hours logic
│   ├── config.py       # Configuration management
│   ├── database.py     # SQLAlchemy models
│   └── cli.py          # Command-line interface
├── scripts/
│   └── check_jobs.py   # Main cron job
├── config/
│   ├── config.yaml.example
│   ├── user_companies.yaml.example
│   └── keywords.yaml
├── data/               # SQLite database (gitignored)
├── logs/               # Log files (gitignored)
├── docs/
│   ├── deployment.md
│   └── operations.md
├── Dockerfile
├── docker-compose.yml
├── job-radar.service   # systemd service
├── job-radar.timer     # systemd timer
├── pyproject.toml
└── .env.example
```

## Commands

```bash
job-radar check              # Run job check now
job-radar status             # Show system status
job-radar companies -l       # List companies
job-radar companies -a       # Add company
job-radar companies -r ID    # Remove company
job-radar test-alerts        # Test all channels
job-radar test-alerts -c telegram  # Test specific channel
job-radar init-db            # Initialize database
job-radar config-show        # Show current config
job-radar config-example     # Show example config
```

## Monitoring

```bash
# View logs
docker-compose logs -f job-radar-cron

# Database stats
sqlite3 data/job_radar.db "SELECT COUNT(*) FROM jobs;"
sqlite3 data/job_radar.db "SELECT * FROM alert_logs ORDER BY sent_at DESC LIMIT 10;"

# Recent alerts
tail -20 data/alerts.log
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Add scrapers for new ATS types
4. Submit PR

## License

MIT License - see LICENSE file for details.

---

**Built with ❤️ for AI job seekers**
