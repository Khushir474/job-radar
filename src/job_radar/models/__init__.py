"""Job Radar - Data Models"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


class ATSType(str, Enum):
    """Supported Applicant Tracking Systems"""
    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    WORKDAY = "workday"
    CUSTOM = "custom"
    ASHby = "ashby"
    BREEZY = "breezy"
    SMARTRECRUITERS = "smartrecruiters"
    JOBLEVER = "joblever"


class ExperienceLevel(str, Enum):
    """Job experience levels"""
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    STAFF = "staff"
    PRINCIPAL = "principal"
    DIRECTOR = "director"
    VP = "vp"


class RoleCategory(str, Enum):
    """Role categories to track"""
    DATA_ANALYST = "data_analyst"
    DATA_SCIENTIST = "data_scientist"
    ML_ENGINEER = "ml_engineer"
    AI_ENGINEER = "ai_engineer"
    RESEARCH_SCIENTIST = "research_scientist"
    APPLIED_SCIENTIST = "applied_scientist"
    ML_RESEARCHER = "ml_researcher"
    DATA_ENGINEER = "data_engineer"
    AI_RESEARCHER = "ai_researcher"


class JobType(str, Enum):
    """Job employment types"""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    TEMPORARY = "temporary"


class Company(BaseModel):
    """Company configuration"""
    id: str = Field(..., description="Unique slug identifier")
    name: str = Field(..., description="Display name")
    career_url: HttpUrl = Field(..., description="Career page URL")
    ats_type: ATSType = Field(..., description="ATS platform type")
    ats_config: dict = Field(default_factory=dict, description="ATS-specific configuration")
    search_keywords: list[str] = Field(default_factory=list, description="Additional search keywords")
    enabled: bool = Field(default=True, description="Whether to scrape this company")
    priority: int = Field(default=1, description="Scraping priority (lower = first)")
    custom_scraper: Optional[str] = Field(default=None, description="Custom scraper class name")
    webhook: Optional[str] = Field(default=None, description="Discord webhook URL for alerts (overrides default)")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_scraped: Optional[datetime] = Field(default=None)
    last_scrape_status: Optional[str] = Field(default=None)
    jobs_found_total: int = Field(default=0)


class Job(BaseModel):
    """Normalized job posting"""
    id: str = Field(..., description="Unique identifier (company + external_id)")
    company_id: str = Field(..., description="Company slug")
    external_id: str = Field(..., description="ATS-provided job ID")
    title: str = Field(..., description="Job title")
    url: HttpUrl = Field(..., description="Job application URL")
    location: str = Field(default="", description="Job location")
    department: Optional[str] = Field(default=None, description="Department/team")
    experience_level: Optional[ExperienceLevel] = Field(default=None)
    job_type: Optional[JobType] = Field(default=None)
    posted_date: Optional[datetime] = Field(default=None)
    description: Optional[str] = Field(default=None, description="Full job description")
    raw_data: dict = Field(default_factory=dict, description="Original scraper output")
    
    # Matched categories
    matched_roles: list[RoleCategory] = Field(default_factory=list)
    matched_keywords: list[str] = Field(default_factory=list)
    
    # Timestamps
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    first_seen_at: datetime = Field(default_factory=datetime.utcnow)
    last_seen_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Status
    is_new: bool = Field(default=True)
    alerted: bool = Field(default=False)
    alerted_at: Optional[datetime] = Field(default=None)
    alerted_channels: list[str] = Field(default_factory=list)


class AlertConfig(BaseModel):
    """Alert channel configuration"""
    # iMessage
    imessage_enabled: bool = False
    imessage_recipients: list[str] = Field(default_factory=list)
    
    # Telegram
    telegram_enabled: bool = False
    telegram_bot_token: Optional[str] = None
    telegram_chat_ids: list[str] = Field(default_factory=list)
    
    # Discord
    discord_enabled: bool = False
    discord_webhook_url: Optional[str] = None
    
    # Email
    email_enabled: bool = False
    email_smtp_host: Optional[str] = None
    email_smtp_port: int = 587
    email_username: Optional[str] = None
    email_password: Optional[str] = None
    email_from: Optional[str] = None
    email_recipients: list[str] = Field(default_factory=list)
    email_use_tls: bool = True
    
    # File
    file_enabled: bool = True
    file_path: str = "data/alerts.log"
    file_format: str = "json"  # json, markdown, txt
    
    # General
    enabled_channels: list[str] = Field(default_factory=lambda: ["file"])
    alert_template: str = "default"
    include_description: bool = True
    max_jobs_per_alert: int = 10


class FilterConfig(BaseModel):
    """Job filtering configuration"""
    roles: list[RoleCategory] = Field(
        default_factory=lambda: [
            RoleCategory.DATA_ANALYST,
            RoleCategory.DATA_SCIENTIST,
            RoleCategory.ML_ENGINEER,
            RoleCategory.AI_ENGINEER,
            RoleCategory.RESEARCH_SCIENTIST,
            RoleCategory.APPLIED_SCIENTIST,
            RoleCategory.ML_RESEARCHER,
        ]
    )
    locations: list[str] = Field(default_factory=lambda: [
        "Remote", "Anywhere", "United States", "USA", "US",
        "San Francisco", "New York", "Seattle", "Boston", "Austin",
        "Los Angeles", "Chicago", "Washington DC", "Denver", "Atlanta"
    ])
    experience_levels: list[ExperienceLevel] = Field(default_factory=list)
    job_types: list[JobType] = Field(default_factory=list)
    excluded_keywords: list[str] = Field(default_factory=lambda: [
        "intern", "internship", "co-op", "coop", "student",
        "entry level", "new grad", "university", "campus"
    ])
    required_keywords: list[str] = Field(default_factory=list)
    min_salary: Optional[int] = Field(default=None)
    max_salary: Optional[int] = Field(default=None)
    currency: str = "USD"


class SchedulerConfig(BaseModel):
    """Scheduler configuration"""
    check_interval_hours: int = 2
    quiet_hours_start: str = "22:00"  # 10 PM
    quiet_hours_end: str = "06:00"    # 6 AM
    timezone: str = "America/Los_Angeles"
    max_concurrent_scrapers: int = 5
    request_timeout: int = 30
    retry_attempts: int = 3
    retry_delay: int = 5
    daily_summary_enabled: bool = True
    daily_summary_time: str = "09:00"


class AppConfig(BaseModel):
    """Main application configuration"""
    # Database
    database_url: str = "sqlite+aiosqlite:///data/job_radar.db"
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/job_radar.log"
    log_format: str = "json"
    
    # Sub-configs
    companies: list[Company] = Field(default_factory=list)
    alerts: AlertConfig = Field(default_factory=AlertConfig)
    filters: FilterConfig = Field(default_factory=FilterConfig)
    scheduler: SchedulerConfig = Field(default_factory=SchedulerConfig)
    
    # Runtime
    user_companies_file: str = "config/user_companies.yaml"
    keywords_file: str = "config/keywords.yaml"