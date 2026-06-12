"""Job Radar - Configuration Management"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from job_radar.models import (
    AppConfig, Company, CompanyDB, RoleCategory, ExperienceLevel,
    ATSType, JobType, AlertConfig, FilterConfig, SchedulerConfig
)
from job_radar.database import DatabaseManager


class Settings(BaseSettings):
    """Environment-based settings"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    # Database
    database_url: str = "sqlite+aiosqlite:///data/job_radar.db"
    
    # Alert credentials (from env)
    telegram_bot_token: Optional[str] = None
    telegram_chat_ids: str = ""
    discord_webhook_url: Optional[str] = None
    email_smtp_host: Optional[str] = None
    email_smtp_port: int = 587
    email_username: Optional[str] = None
    email_password: Optional[str] = None
    email_from: Optional[str] = None
    email_recipients: str = ""
    
    # iMessage (macOS only)
    imessage_recipients: str = ""
    
    # Scheduler
    check_interval_hours: int = 2
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "06:00"
    timezone: str = "America/Los_Angeles"
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/job_radar.log"


# Built-in top AI companies (30+)
BUILTIN_COMPANIES = [
    Company(
        id="openai",
        name="OpenAI",
        career_url="https://openai.com/careers",
        ats_type=ATSType.GREENHOUSE,
        ats_config={"board_token": "openai"},
        priority=1,
    ),
    Company(
        id="anthropic",
        name="Anthropic",
        career_url="https://www.anthropic.com/careers",
        ats_type=ATSType.GREENHOUSE,
        ats_config={"board_token": "anthropic"},
        priority=1,
    ),
    Company(
        id="deepmind",
        name="Google DeepMind",
        career_url="https://deepmind.google/careers/",
        ats_type=ATSType.CUSTOM,
        ats_config={"base_url": "https://deepmind.google/careers/"},
        priority=1,
    ),
    Company(
        id="meta-ai",
        name="Meta AI",
        career_url="https://www.metacareers.com/jobs?teams=AI%20Research",
        ats_type=ATSType.CUSTOM,
        ats_config={"base_url": "https://www.metacareers.com"},
        priority=1,
    ),
    Company(
        id="microsoft-research",
        name="Microsoft Research",
        career_url="https://www.microsoft.com/en-us/research/careers/",
        ats_type=ATSType.CUSTOM,
        ats_config={"base_url": "https://careers.microsoft.com"},
        priority=1,
    ),
    Company(
        id="nvidia",
        name="NVIDIA",
        career_url="https://www.nvidia.com/en-us/about-nvidia/careers/",
        ats_type=ATSType.WORKDAY,
        ats_config={"tenant": "nvidia", "career_site": "nvidia"},
        priority=1,
    ),
    Company(
        id="apple-ml",
        name="Apple Machine Learning",
        career_url="https://machinelearning.apple.com/",
        ats_type=ATSType.CUSTOM,
        ats_config={"base_url": "https://jobs.apple.com"},
        priority=1,
    ),
    Company(
        id="amazon-science",
        name="Amazon Science",
        career_url="https://www.amazon.science/careers",
        ats_type=ATSType.CUSTOM,
        ats_config={"base_url": "https://www.amazon.jobs"},
        priority=1,
    ),
    Company(
        id="tesla-ai",
        name="Tesla AI",
        career_url="https://www.tesla.com/careers/search?department=AI%20%26%20Robotics",
        ats_type=ATSType.CUSTOM,
        ats_config={"base_url": "https://www.tesla.com/careers"},
        priority=1,
    ),
    Company(
        id="adobe-research",
        name="Adobe Research",
        career_url="https://research.adobe.com/careers/",
        ats_type=ATSType.CUSTOM,
        ats_config={"base_url": "https://adobe.wd1.myworkdayjobs.com"},
        priority=2,
    ),
    Company(
        id="huggingface",
        name="Hugging Face",
        career_url="https://huggingface.co/careers",
        ats_type=ATSType.GREENHOUSE,
        ats_config={"board_token": "huggingface"},
        priority=1,
    ),
    Company(
        id="cohere",
        name="Cohere",
        career_url="https://cohere.com/careers",
        ats_type=ATSType.GREENHOUSE,
        ats_config={"board_token": "cohere"},
        priority=1,
    ),
    Company(
        id="mistral-ai",
        name="Mistral AI",
        career_url="https://www.mistral.ai/careers",
        ats_type=ATSType.GREENHOUSE,
        ats_config={"board_token": "mistralai"},
        priority=1,
    ),
    Company(
        id="perplexity",
        name="Perplexity",
        career_url="https://www.perplexity.ai/careers",
        ats_type=ATSType.GREENHOUSE,
        ats_config={"board_token": "perplexity"},
        priority=1,
    ),
    Company(
        id="databricks",
        name="Databricks",
        career_url="https://www.databricks.com/company/careers",
        ats_type=ATSType.WORKDAY,
        ats_config={"tenant": "databricks", "career_site": "external"},
        priority=1,
    ),
    Company(
        id="palantir",
        name="Palantir",
        career_url="https://www.palantir.com/careers/",
        ats_type=ATSType.CUSTOM,
        ats_config={"base_url": "https://www.palantir.com/careers"},
        priority=1,
    ),
    Company(
        id="scale-ai",
        name="Scale AI",
        career_url="https://scale.com/careers",
        ats_type=ATSType.GREENHOUSE,
        ats_config={"board_token": "scaleai"},
        priority=1,
    ),
    Company(
        id="weights-biases",
        name="Weights & Biases",
        career_url="https://wandb.ai/careers",
        ats_type=ATSType.GREENHOUSE,
        ats_config={"board_token": "wandb"},
        priority=2,
    ),
    Company(
        id="langchain",
        name="LangChain",
        career_url="https://www.langchain.com/careers",
        ats_type=ATSType.GREENHOUSE,
        ats_config={"board_token": "langchain"},
        priority=1,
    ),
    Company(
        id="runway",
        name="Runway",
        career_url="https://runwayml.com/careers",
        ats_type=ATSType.GREENHOUSE,
        ats_config={"board_token": "runwayml"},
        priority=1,
    ),
    Company(
        id="stability-ai",
        name="Stability AI",
        career_url="https://stability.ai/careers",
        ats_type=ATSType.GREENHOUSE,
        ats_config={"board_token": "stabilityai"},
        priority=1,
    ),
    Company(
        id="midjourney",
        name="Midjourney",
        career_url="https://www.midjourney.com/jobs/",
        ats_type=ATSType.CUSTOM,
        ats_config={"base_url": "https://www.midjourney.com/jobs"},
        priority=2,
    ),
    Company(
        id="elevenlabs",
        name="ElevenLabs",
        career_url="https://elevenlabs.io/careers",
        ats_type=ATSType.GREENHOUSE,
        ats_config={"board_token": "elevenlabs"},
        priority=1,
    ),
    Company(
        id="replicate",
        name="Replicate",
        career_url="https://replicate.com/careers",
        ats_type=ATSType.GREENHOUSE,
        ats_config={"board_token": "replicate"},
        priority=1,
    ),
    Company(
        id="modal",
        name="Modal",
        career_url="https://modal.com/careers",
        ats_type=ATSType.GREENHOUSE,
        ats_config={"board_token": "modal"},
        priority=1,
    ),
    Company(
        id="together-ai",
        name="Together AI",
        career_url="https://www.together.ai/careers",
        ats_type=ATSType.GREENHOUSE,
        ats_config={"board_token": "togetherai"},
        priority=1,
    ),
    Company(
        id="fireworks-ai",
        name="Fireworks AI",
        career_url="https://fireworks.ai/careers",
        ats_type=ATSType.GREENHOUSE,
        ats_config={"board_token": "fireworksai"},
        priority=1,
    ),
    Company(
        id="anyscale",
        name="Anyscale",
        career_url="https://www.anyscale.com/careers",
        ats_type=ATSType.GREENHOUSE,
        ats_config={"board_token": "anyscale"},
        priority=1,
    ),
    Company(
        id="mosaicml",
        name="MosaicML (Databricks)",
        career_url="https://www.mosaicml.com/careers",
        ats_type=ATSType.GREENHOUSE,
        ats_config={"board_token": "mosaicml"},
        priority=2,
    ),
    Company(
        id="cohere",
        name="Cohere",
        career_url="https://cohere.com/careers",
        ats_type=ATSType.GREENHOUSE,
        ats_config={"board_token": "cohere"},
        priority=1,
    ),
    Company(
        id="adept",
        name="Adept",
        career_url="https://www.adept.ai/careers",
        ats_type=ATSType.GREENHOUSE,
        ats_config={"board_token": "adept"},
        priority=2,
    ),
    Company(
        id="character-ai",
        name="Character.AI",
        career_url="https://character.ai/careers",
        ats_type=ATSType.GREENHOUSE,
        ats_config={"board_token": "characterai"},
        priority=1,
    ),
    Company(
        id="inflection",
        name="Inflection AI",
        career_url="https://inflection.ai/careers",
        ats_type=ATSType.GREENHOUSE,
        ats_config={"board_token": "inflectionai"},
        priority=2,
    ),
]


DEFAULT_KEYWORDS = {
    RoleCategory.DATA_ANALYST: [
        "data analyst", "business analyst", "analytics analyst",
        "data analytics", "reporting analyst", "bi analyst",
        "business intelligence", "data visualization", "tableau",
        "power bi", "looker", "sql analyst"
    ],
    RoleCategory.DATA_SCIENTIST: [
        "data scientist", "applied scientist", "research scientist",
        "machine learning scientist", "ml scientist", "data science",
        "statistical modeling", "predictive modeling", "experimentation",
        "causal inference", "ab testing"
    ],
    RoleCategory.ML_ENGINEER: [
        "machine learning engineer", "ml engineer", "ml platform engineer",
        "ml infrastructure", "model deployment", "mlops", "ml ops",
        "feature store", "model serving", "training pipeline",
        "kubeflow", "mlflow", "ray", "vertex ai", "sagemaker"
    ],
    RoleCategory.AI_ENGINEER: [
        "ai engineer", "artificial intelligence engineer",
        "llm engineer", "large language model", "generative ai engineer",
        "prompt engineer", "rag engineer", "ai platform engineer",
        "foundation model", "fine-tuning", "llm ops"
    ],
    RoleCategory.RESEARCH_SCIENTIST: [
        "research scientist", "ai researcher", "ml researcher",
        "deep learning researcher", "computer vision researcher",
        "nlp researcher", "reinforcement learning researcher",
        "foundational research", "ai safety", "alignment"
    ],
    RoleCategory.APPLIED_SCIENTIST: [
        "applied scientist", "applied ml scientist", "applied ai scientist",
        "machine learning applied scientist", "production ml"
    ],
    RoleCategory.ML_RESEARCHER: [
        "ml researcher", "machine learning researcher", "ai ml researcher",
        "deep learning engineer", "neural network researcher"
    ],
    RoleCategory.DATA_ENGINEER: [
        "data engineer", "data platform engineer", "etl engineer",
        "data pipeline", "spark engineer", "kafka engineer",
        "airflow", "dbt", "snowflake", "bigquery", "redshift"
    ],
    RoleCategory.AI_RESEARCHER: [
        "ai researcher", "artificial intelligence researcher",
        "foundation model researcher", "agi researcher"
    ],
}


DEFAULT_EXCLUDED_KEYWORDS = [
    "intern", "internship", "co-op", "coop", "student",
    "entry level", "new grad", "university", "campus",
    "fellow", "fellowship", "apprentice", "apprenticeship",
    "volunteer", "unpaid", "contract to hire"
]


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/config.yaml"
        self.user_companies_path = "config/user_companies.yaml"
        self.keywords_path = "config/keywords.yaml"
        self.settings = Settings()
        self._config: Optional[AppConfig] = None
    
    def load_config(self) -> AppConfig:
        """Load configuration from file and environment"""
        if self._config is not None:
            return self._config
        
        # Start with defaults
        config = AppConfig(
            database_url=self.settings.database_url,
            log_level=self.settings.log_level,
            log_file=self.settings.log_file,
        )
        
        # Load from YAML if exists
        if Path(self.config_path).exists():
            with open(self.config_path) as f:
                file_config = yaml.safe_load(f) or {}
            
            # Merge file config
            if "alerts" in file_config:
                config.alerts = AlertConfig(**file_config["alerts"])
            if "filters" in file_config:
                config.filters = FilterConfig(**file_config["filters"])
            if "scheduler" in file_config:
                config.scheduler = SchedulerConfig(**file_config["scheduler"])
            if "companies" in file_config:
                config.companies = [Company(**c) for c in file_config["companies"]]
        
        # Override with environment variables
        self._apply_env_overrides(config)
        
        # Load built-in companies if none configured
        if not config.companies:
            config.companies = BUILTIN_COMPANIES
        
        # Load user companies
        user_companies = self.load_user_companies()
        config.companies.extend(user_companies)
        
        self._config = config
        return config
    
    def _apply_env_overrides(self, config: AppConfig) -> None:
        """Apply environment variable overrides"""
        # Alerts
        if self.settings.telegram_bot_token:
            config.alerts.telegram_enabled = True
            config.alerts.telegram_bot_token = self.settings.telegram_bot_token
        if self.settings.telegram_chat_ids:
            config.alerts.telegram_chat_ids = [
                c.strip() for c in self.settings.telegram_chat_ids.split(",")
            ]
        if self.settings.discord_webhook_url:
            config.alerts.discord_enabled = True
            config.alerts.discord_webhook_url = self.settings.discord_webhook_url
        if self.settings.email_smtp_host:
            config.alerts.email_enabled = True
            config.alerts.email_smtp_host = self.settings.email_smtp_host
            config.alerts.email_smtp_port = self.settings.email_smtp_port
            config.alerts.email_username = self.settings.email_username
            config.alerts.email_password = self.settings.email_password
            config.alerts.email_from = self.settings.email_from
        if self.settings.email_recipients:
            config.alerts.email_recipients = [
                e.strip() for e in self.settings.email_recipients.split(",")
            ]
        if self.settings.imessage_recipients:
            config.alerts.imessage_enabled = True
            config.alerts.imessage_recipients = [
                r.strip() for r in self.settings.imessage_recipients.split(",")
            ]
        
        # Scheduler
        config.scheduler.check_interval_hours = self.settings.check_interval_hours
        config.scheduler.quiet_hours_start = self.settings.quiet_hours_start
        config.scheduler.quiet_hours_end = self.settings.quiet_hours_end
        config.scheduler.timezone = self.settings.timezone
        
        # Logging
        config.log_level = self.settings.log_level
        config.log_file = self.settings.log_file
    
    def load_user_companies(self) -> list[Company]:
        """Load user-added companies from YAML file"""
        if not Path(self.user_companies_path).exists():
            return []
        
        with open(self.user_companies_path) as f:
            data = yaml.safe_load(f) or {}
        
        companies = []
        for c in data.get("companies", []):
            try:
                companies.append(Company(**c))
            except ValidationError as e:
                print(f"Warning: Invalid user company config: {e}")
        
        return companies
    
    def save_user_company(self, company: Company) -> None:
        """Save a user company to YAML file"""
        Path(self.user_companies_path).parent.mkdir(parents=True, exist_ok=True)
        
        data = {"companies": []}
        if Path(self.user_companies_path).exists():
            with open(self.user_companies_path) as f:
                data = yaml.safe_load(f) or {"companies": []}
        
        # Check if already exists
        existing = next((c for c in data["companies"] if c.get("id") == company.id), None)
        if existing:
            data["companies"].remove(existing)
        
        data["companies"].append(company.model_dump())
        
        with open(self.user_companies_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    def remove_user_company(self, company_id: str) -> bool:
        """Remove a user company"""
        if not Path(self.user_companies_path).exists():
            return False
        
        with open(self.user_companies_path) as f:
            data = yaml.safe_load(f) or {"companies": []}
        
        original_len = len(data["companies"])
        data["companies"] = [c for c in data["companies"] if c.get("id") != company_id]
        
        if len(data["companies"]) < original_len:
            with open(self.user_companies_path, "w") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            return True
        return False
    
    def load_keywords(self) -> dict[RoleCategory, list[str]]:
        """Load role keywords from YAML"""
        if Path(self.keywords_path).exists():
            with open(self.keywords_path) as f:
                data = yaml.safe_load(f) or {}
            return {
                RoleCategory(k): v for k, v in data.items()
                if k in RoleCategory.__members__
            }
        return DEFAULT_KEYWORDS
    
    def save_config(self, config: AppConfig) -> None:
        """Save configuration to YAML file"""
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "database_url": config.database_url,
            "log_level": config.log_level,
            "log_file": config.log_file,
            "alerts": config.alerts.model_dump(),
            "filters": config.filters.model_dump(),
            "scheduler": config.scheduler.model_dump(),
            "companies": [c.model_dump() for c in config.companies],
        }
        
        with open(self.config_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def create_example_config() -> str:
    """Generate example configuration"""
    config = AppConfig()
    config.alerts.telegram_enabled = True
    config.alerts.telegram_bot_token = "YOUR_BOT_TOKEN"
    config.alerts.telegram_chat_ids = ["-1001234567890"]
    config.alerts.discord_enabled = True
    config.alerts.discord_webhook_url = "https://discord.com/api/webhooks/..."
    config.alerts.email_enabled = True
    config.alerts.email_smtp_host = "smtp.gmail.com"
    config.alerts.email_smtp_port = 587
    config.alerts.email_username = "your_email@gmail.com"
    config.alerts.email_password = "your_app_password"
    config.alerts.email_from = "Job Radar <your_email@gmail.com>"
    config.alerts.email_recipients = ["you@example.com"]
    config.alerts.imessage_enabled = True
    config.alerts.imessage_recipients = ["+15551234567"]
    
    import yaml
    return yaml.dump(config.model_dump(), default_flow_style=False, sort_keys=False)