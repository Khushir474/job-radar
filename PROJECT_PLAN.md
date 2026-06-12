# Job Radar - Job Alert Automation Project

## Project Overview
Automated job monitoring system that tracks Data Analyst (DA), Data Scientist (DS), Machine Learning (ML), and AI roles at 30+ top AI companies plus user-defined companies. Sends alerts via iMessage, Telegram, Discord, email, and file every 2 hours with quiet hours from 10 PM to 6 AM PST.

---

## Requirements

### Functional Requirements

#### 1. Company Database
- **Core Companies (30+ top AI companies):**
  - OpenAI, Anthropic, Google DeepMind, Meta AI, Microsoft Research
  - NVIDIA, Apple ML, Amazon Science, Tesla AI, Adobe Research
  - Hugging Face, Cohere, Mistral AI, Perplexity, Databricks
  - Snowflake, Palantir, Scale AI, Weights & Biases, LangChain
  - Runway, Stability AI, Midjourney, ElevenLabs, Replicate
  - Modal, Together AI, Fireworks AI, Anyscale, MosaicML
  - + 5 more emerging AI companies
- **User-Defined Companies:** Configurable via config file / CLI / web UI
- **Company Metadata:** Name, career page URL, ATS type (Greenhouse, Lever, Workday, custom), search keywords

#### 2. Job Filtering
- **Roles to Track:** Data Analyst, Data Scientist, ML Engineer, AI Engineer, Research Scientist, Applied Scientist, ML Researcher
- **Keywords:** Configurable per role category (DA/DS/ML/AI)
- **Location Filtering:** Remote, hybrid, on-site preferences
- **Experience Level:** Entry, mid, senior, staff, principal
- **Deduplication:** Track seen job IDs to avoid duplicate alerts

#### 3. Alert Channels
- **iMessage:** via `imsg` CLI (macOS only)
- **Telegram:** via Hermes gateway / Bot API
- **Discord:** via Hermes gateway / webhook
- **Email:** via SMTP (Himalaya CLI or Python smtplib)
- **File:** Local JSON/Markdown log for review
- **Channel Selection:** Per-user configurable (enable/disable per channel)

#### 4. Scheduling
- **Frequency:** Every 2 hours during active hours
- **Quiet Hours:** 10 PM - 6 AM PST (configurable timezone)
- **Manual Trigger:** CLI command to run check immediately
- **Status Reporting:** Daily summary of jobs found/alerted

#### 5. Data Storage
- **Job Records:** SQLite database (local, portable)
- **Seen Jobs:** Track job IDs with timestamps
- **Company Config:** JSON/YAML config file
- **User Preferences:** Alert channels, filters, quiet hours
- **Logs:** Structured logging for debugging

### Non-Functional Requirements
- **Reliability:** Handle network failures, rate limits, site changes
- **Performance:** Complete check cycle within 5 minutes
- **Maintainability:** Modular scrapers per company/ATS
- **Extensibility:** Easy to add new companies/channels
- **Observability:** Logging, metrics, error tracking

---

## Sprint Plan

### Sprint 1: Foundation (Week 1)
**Goal:** Project structure, config, storage, company database

| Task | Description | Deliverable |
|------|-------------|-------------|
| 1.1 | Initialize Python project with poetry/uv | `pyproject.toml`, venv |
| 1.2 | Create config schema (Pydantic models) | `config.yaml` schema |
| 1.3 | Set up SQLite database with migrations | `database.py`, schema |
| 1.4 | Build company database (30+ AI companies) | `companies.json` |
| 1.5 | Create user company input CLI | `cli.py add-company` |
| 1.6 | Basic project structure and logging | `src/job_radar/` |

### Sprint 2: Scraping Engine (Week 2)
**Goal:** Robust job scraping for multiple ATS types

| Task | Description | Deliverable |
|------|-------------|-------------|
| 2.1 | Base scraper interface + HTTP client | `scrapers/base.py` |
| 2.2 | Greenhouse scraper | `scrapers/greenhouse.py` |
| 2.3 | Lever scraper | `scrapers/lever.py` |
| 2.4 | Workday scraper (basic) | `scrapers/workday.py` |
| 2.5 | Custom/scrapy-based scrapers for others | `scrapers/custom.py` |
| 2.6 | Rate limiting, retry, error handling | `scrapers/utils.py` |
| 2.7 | Job parsing and normalization | `models/job.py` |
| 2.8 | Integration test with real companies | Test results |

### Sprint 3: Filtering & Deduplication (Week 2-3)
**Goal:** Smart job matching and duplicate prevention

| Task | Description | Deliverable |
|------|-------------|-------------|
| 3.1 | Role keyword configuration | `config/keywords.yaml` |
| 3.2 | Job matching engine (role, location, level) | `matcher.py` |
| 3.3 | Seen job tracking with SQLite | `storage/seen_jobs.py` |
| 3.4 | Fuzzy matching for similar postings | `matcher/fuzzy.py` |
| 3.5 | Configurable filter profiles | `config/filters.yaml` |

### Sprint 4: Alert System (Week 3)
**Goal:** Multi-channel alert delivery

| Task | Description | Deliverable |
|------|-------------|-------------|
| 4.1 | Alert formatter (Markdown, plain text) | `alerts/formatter.py` |
| 4.2 | iMessage sender (imsg CLI) | `alerts/imessage.py` |
| 4.3 | Telegram sender (Bot API) | `alerts/telegram.py` |
| 4.4 | Discord sender (webhook) | `alerts/discord.py` |
| 4.5 | Email sender (SMTP) | `alerts/email.py` |
| 4.6 | File logger (JSON/Markdown) | `alerts/file_logger.py` |
| 4.7 | Channel manager (enable/disable per user) | `alerts/manager.py` |
| 4.8 | Alert deduplication (per channel) | `alerts/dedup.py` |

### Sprint 5: Cron Integration & Scheduling (Week 3-4)
**Goal:** Hermes cron jobs with quiet hours

| Task | Description | Deliverable |
|------|-------------|-------------|
| 5.1 | Main check job script | `scripts/check_jobs.py` |
| 5.2 | Quiet hours logic (PST timezone) | `scheduler/quiet_hours.py` |
| 5.3 | Hermes cron job creation | `hermes cron create` commands |
| 5.4 | Daily summary job | `scripts/daily_summary.py` |
| 5.5 | Manual trigger CLI | `cli.py check-now` |
| 5.6 | Status/health check endpoint | `scripts/health_check.py` |

### Sprint 6: Deployment & Operations (Week 4)
**Goal:** 24/7 deployment options and documentation

| Task | Description | Deliverable |
|------|-------------|-------------|
| 6.1 | Dockerfile for containerization | `Dockerfile` |
| 6.2 | Docker Compose for local dev | `docker-compose.yml` |
| 6.3 | Cloud deployment guides (VPS, Railway, Fly.io, Modal) | `docs/deployment.md` |
| 6.4 | Systemd service for Linux VPS | `job-radar.service` |
| 6.5 | Environment variable template | `.env.example` |
| 6.6 | Monitoring/alerting for the monitor | `docs/operations.md` |
| 6.7 | README with full setup guide | `README.md` |

### Sprint 7: Testing & Polish (Week 4-5)
**Goal:** End-to-end testing, bug fixes, push to GitHub

| Task | Description | Deliverable |
|------|-------------|-------------|
| 7.1 | Unit tests for core modules | `tests/` |
| 7.2 | Integration test with real companies | Test run logs |
| 7.3 | Load test (30+ companies) | Performance metrics |
| 7.4 | Bug fixes and edge cases | GitHub issues closed |
| 7.5 | Final push to GitHub | `git push origin main` |

---

## Technical Architecture

```
job-radar/
├── src/job_radar/
│   ├── __init__.py
│   ├── config.py          # Pydantic config models
│   ├── database.py        # SQLite setup + migrations
│   ├── models/
│   │   ├── __init__.py
│   │   ├── job.py         # Job dataclass
│   │   ├── company.py     # Company dataclass
│   │   └── alert.py       # Alert dataclass
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base.py        # BaseScraper ABC
│   │   ├── greenhouse.py
│   │   ├── lever.py
│   │   ├── workday.py
│   │   ├── custom.py
│   │   └── registry.py    # Company -> Scraper mapping
│   ├── matcher/
│   │   ├── __init__.py
│   │   ├── engine.py      # Job matching logic
│   │   ├── keywords.py    # Role keywords
│   │   └── fuzzy.py       # Fuzzy matching
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── seen_jobs.py   # Deduplication
│   │   └── companies.py   # Company CRUD
│   ├── alerts/
│   │   ├── __init__.py
│   │   ├── formatter.py
│   │   ├── manager.py
│   │   ├── imessage.py
│   │   ├── telegram.py
│   │   ├── discord.py
│   │   ├── email.py
│   │   ├── file_logger.py
│   │   └── dedup.py
│   ├── scheduler/
│   │   ├── __init__.py
│   │   ├── quiet_hours.py
│   │   └── cron_jobs.py
│   └── cli.py             # Typer/Click CLI
├── scripts/
│   ├── check_jobs.py      # Main cron job
│   ├── daily_summary.py
│   └── health_check.py
├── config/
│   ├── config.yaml.example
│   ├── companies.json     # 30+ AI companies
│   ├── keywords.yaml      # Role keywords
│   └── filters.yaml       # Filter profiles
├── data/                  # SQLite DB (gitignored)
├── logs/                  # Log files (gitignored)
├── tests/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── .env.example
├── README.md
└── docs/
    ├── deployment.md
    └── operations.md
```

---

## Data Models

### Company
```python
class Company(BaseModel):
    id: str                    # slug: "openai"
    name: str                  # "OpenAI"
    career_url: str            # "https://openai.com/careers"
    ats_type: ATSType          # GREENHOUSE, LEVER, WORKDAY, CUSTOM
    ats_config: dict           # e.g., {"board_token": "openai"} for Greenhouse
    search_keywords: list[str] # Additional keywords
    enabled: bool = True
    priority: int = 1          # Check order
```

### Job
```python
class Job(BaseModel):
    id: str                    # Unique ID (company + external_id)
    company_id: str
    title: str
    url: str
    location: str
    department: str | None
    experience_level: ExperienceLevel | None
    posted_date: datetime | None
    description: str | None
    raw_data: dict             # Original scraper output
    scraped_at: datetime
```

### UserConfig
```python
class UserConfig(BaseModel):
    # Alert channels
    imessage_enabled: bool = False
    imessage_recipients: list[str] = []
    telegram_enabled: bool = False
    telegram_bot_token: str | None = None
    telegram_chat_ids: list[str] = []
    discord_enabled: bool = False
    discord_webhook_url: str | None = None
    email_enabled: bool = False
    email_smtp_host: str | None = None
    email_smtp_port: int = 587
    email_username: str | None = None
    email_password: str | None = None
    email_recipients: list[str] = []
    file_enabled: bool = True
    file_path: str = "data/alerts.log"
    
    # Filters
    roles: list[Role] = [Role.DA, Role.DS, Role.ML, Role.AI]
    locations: list[str] = ["Remote", "San Francisco", "New York", "Seattle"]
    experience_levels: list[ExperienceLevel] = []
    excluded_keywords: list[str] = []
    
    # Scheduling
    check_interval_hours: int = 2
    quiet_hours_start: str = "22:00"  # 10 PM
    quiet_hours_end: str = "06:00"    # 6 AM
    timezone: str = "America/Los_Angeles"
```

---

## Answers to Your Questions

### 1. Best Way to Receive and Store User-Inputted Companies?

**Recommended Approach: Config File + CLI + Optional Web UI**

| Method | Pros | Cons |
|--------|------|------|
| **YAML/JSON config file** | Version controlled, simple, no DB needed | Manual edit required |
| **CLI (`job-radar add-company`)** | Interactive, validates input, updates config | Requires terminal access |
| **SQLite database** | Queryable, extensible, supports metadata | Slightly more complex |
| **Web UI (optional future)** | User-friendly, accessible from phone | More infrastructure |

**Implementation:**
- Primary: `config/user_companies.yaml` (version controlled, easy to backup)
- CLI: `job-radar companies add --name "Acme AI" --url "https://acme.ai/careers" --ats greenhouse --board-token "acme"`
- Stores in SQLite for querying + exports to YAML for git sync
- Supports bulk import from CSV/JSON

### 2. Will Cron Jobs Require My Local Machine to Be On?

**YES - Hermes cron runs on the machine where Hermes is running.**

If your laptop is off/sleeping, the cron jobs **will not run**. Hermes cron is a local scheduler, not a cloud service.

### 3. Options for 24/7 Operation (Laptop Off)

| Option | Cost | Complexity | Reliability | Best For |
|--------|------|------------|-------------|----------|
| **VPS (DigitalOcean, Linode, Hetzner)** | $4-6/mo | Medium | High | Full control, always on |
| **Railway.app** | $5/mo | Low | High | Quick deploy, git-based |
| **Fly.io** | ~$5/mo | Low-Med | High | Global, Docker-native |
| **Modal.com** | Pay-per-use | Low | High | Serverless, scales to zero |
| **GitHub Actions (scheduled)** | Free | Low | Medium | Limited to 6hr max, no persistence |
| **AWS Lambda + EventBridge** | ~$1/mo | Medium | High | Serverless, enterprise |
| **GCP Cloud Run** | ~$1-5/mo | Medium | High | Serverless containers |
| **Home server / Raspberry Pi** | Hardware cost | Medium | Medium (power/internet) | Local control, no monthly cost |
| **Hermes Gateway on VPS** | VPS cost | Medium | High | Also enables messaging platforms |

**Recommended for You:**
1. **Quick start:** Railway.app or Fly.io - deploy in 10 mins, $5/mo
2. **Cheapest:** GitHub Actions (free) - but limited to 6hr runs, no SQLite persistence between runs
3. **Best control:** $4-6 VPS (Hetzner CX22, DigitalOcean Basic) - full Linux, systemd, persistent storage
4. **Serverless:** Modal.com - pay only when running, scales to zero

**For this project, I'll provide:**
- Dockerfile for containerization
- Docker Compose for local dev
- Railway/Fly.io/Modal deploy configs
- Systemd service file for VPS
- GitHub Actions workflow (as free backup)

---

## Next Steps

1. **Review and approve this plan**
2. **Choose deployment target** (VPS, Railway, Fly.io, Modal, etc.)
3. **Provide alert channel credentials** (or I'll use placeholders)
4. **Start Sprint 1 implementation**

---

*Generated: $(date)*
*Project: job-radar*
*Repository: https://github.com/Khushir474/job-radar*