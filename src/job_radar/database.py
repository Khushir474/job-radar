"""Job Radar - Database Layer"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator, Optional

from sqlalchemy import (
    Column, String, Text, DateTime, Integer, Boolean, JSON, Index, ForeignKey, select
)
from sqlalchemy.ext.asyncio import (
    AsyncSession, async_sessionmaker, create_async_engine
)
from sqlalchemy.orm import DeclarativeBase, relationship

from job_radar.models import (
    Company, Job, RoleCategory, ExperienceLevel, JobType, ATSType
)


class Base(DeclarativeBase):
    pass


class CompanyDB(Base):
    __tablename__ = "companies"
    
    id = Column(String(100), primary_key=True)
    name = Column(String(200), nullable=False)
    career_url = Column(String(500), nullable=False)
    ats_type = Column(String(50), nullable=False)
    ats_config = Column(JSON, default={})
    search_keywords = Column(JSON, default=[])
    enabled = Column(Boolean, default=True)
    priority = Column(Integer, default=1)
    custom_scraper = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_scraped = Column(DateTime, nullable=True)
    last_scrape_status = Column(String(100), nullable=True)
    jobs_found_total = Column(Integer, default=0)
    
    jobs = relationship("JobDB", back_populates="company", lazy="dynamic")
    
    __table_args__ = (
        Index("ix_companies_enabled_priority", "enabled", "priority"),
    )


class JobDB(Base):
    __tablename__ = "jobs"
    
    id = Column(String(200), primary_key=True)
    company_id = Column(String(100), ForeignKey("companies.id"), nullable=False)
    external_id = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False)
    location = Column(String(200), default="")
    department = Column(String(200), nullable=True)
    experience_level = Column(String(50), nullable=True)
    job_type = Column(String(50), nullable=True)
    posted_date = Column(DateTime, nullable=True)
    description = Column(Text, nullable=True)
    raw_data = Column(JSON, default={})
    
    matched_roles = Column(JSON, default=[])
    matched_keywords = Column(JSON, default=[])
    
    scraped_at = Column(DateTime, default=datetime.utcnow)
    first_seen_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    is_new = Column(Boolean, default=True)
    alerted = Column(Boolean, default=False)
    alerted_at = Column(DateTime, nullable=True)
    alerted_channels = Column(JSON, default=[])
    
    company = relationship("CompanyDB", back_populates="jobs")
    
    __table_args__ = (
        Index("ix_jobs_company_id", "company_id"),
        Index("ix_jobs_is_new_alerted", "is_new", "alerted"),
        Index("ix_jobs_scraped_at", "scraped_at"),
        Index("ix_jobs_external_id", "company_id", "external_id", unique=True),
    )


class SeenJobDB(Base):
    """Deduplication tracking"""
    __tablename__ = "seen_jobs"
    
    id = Column(String(200), primary_key=True)  # company_id:external_id
    company_id = Column(String(100), nullable=False)
    external_id = Column(String(100), nullable=False)
    job_title = Column(String(500))
    job_url = Column(String(1000))
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    alert_count = Column(Integer, default=0)
    last_alerted = Column(DateTime, nullable=True)
    alerted_channels = Column(JSON, default=[])
    
    __table_args__ = (
        Index("ix_seen_jobs_company", "company_id"),
    )


class AlertLogDB(Base):
    """Alert delivery logging"""
    __tablename__ = "alert_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(200), nullable=False)
    channel = Column(String(50), nullable=False)
    recipient = Column(String(200), nullable=True)
    status = Column(String(50), nullable=False)  # sent, failed, skipped
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("ix_alert_logs_job_id", "job_id"),
        Index("ix_alert_logs_sent_at", "sent_at"),
    )


class UserCompanyDB(Base):
    """User-added companies"""
    __tablename__ = "user_companies"

    id = Column(String(100), primary_key=True)
    name = Column(String(200), nullable=False)
    career_url = Column(String(500), nullable=False)
    ats_type = Column(String(50), nullable=False)
    ats_config = Column(JSON, default={})
    search_keywords = Column(JSON, default=[])
    enabled = Column(Boolean, default=True)
    priority = Column(Integer, default=10)  # Lower priority than built-in
    custom_scraper = Column(String(100), nullable=True)
    webhook = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_scraped = Column(DateTime, nullable=True)
    last_scrape_status = Column(String(100), nullable=True)
    jobs_found_total = Column(Integer, default=0)
    
    __table_args__ = (
        Index("ix_user_companies_enabled", "enabled"),
    )


class DatabaseManager:
    """Async database manager"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_async_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
        )
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    
    async def init_db(self) -> None:
        """Initialize database tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def close(self) -> None:
        """Close database connections"""
        await self.engine.dispose()
    
    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session"""
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    # Company operations
    async def upsert_company(self, company: Company) -> CompanyDB:
        async with self.session() as session:
            db_company = await session.get(CompanyDB, company.id)
            if db_company:
                for key, value in company.model_dump().items():
                    if key != "id":
                        setattr(db_company, key, value)
                db_company.updated_at = datetime.utcnow()
            else:
                db_company = CompanyDB(**company.model_dump())
                session.add(db_company)
            await session.flush()
            return db_company
    
    async def get_company(self, company_id: str) -> Optional[CompanyDB]:
        async with self.session() as session:
            return await session.get(CompanyDB, company_id)
    
    async def get_enabled_companies(self) -> list[CompanyDB | UserCompanyDB]:
        async with self.session() as session:
            # Get from both built-in and user companies tables
            builtin = await session.execute(
                select(CompanyDB)
                .where(CompanyDB.enabled == True)
                .order_by(CompanyDB.priority)
            )
            user = await session.execute(
                select(UserCompanyDB)
                .where(UserCompanyDB.enabled == True)
                .order_by(UserCompanyDB.priority)
            )
            companies = list(builtin.scalars().all()) + list(user.scalars().all())
            return sorted(companies, key=lambda c: c.priority)
    
    async def update_company_scrape_status(
        self, company_id: str, status: str, jobs_found: int = 0
    ) -> None:
        async with self.session() as session:
            db_company = await session.get(CompanyDB, company_id)
            if db_company:
                db_company.last_scraped = datetime.utcnow()
                db_company.last_scrape_status = status
                db_company.jobs_found_total += jobs_found
    
    # Job operations
    async def upsert_job(self, job: Job) -> JobDB:
        async with self.session() as session:
            db_job = await session.get(JobDB, job.id)
            if db_job:
                db_job.last_seen_at = datetime.utcnow()
                db_job.is_new = False
                for key, value in job.model_dump(exclude={"id", "first_seen_at"}).items():
                    if key == "url":
                        setattr(db_job, key, str(value))
                    else:
                        setattr(db_job, key, value)
            else:
                data = job.model_dump()
                data['url'] = str(job.url)
                db_job = JobDB(**data)
                session.add(db_job)
            await session.flush()
            return db_job
    
    async def get_new_jobs(self, limit: int = 100) -> list[JobDB]:
        async with self.session() as session:
            result = await session.execute(
                select(JobDB)
                .where(JobDB.is_new == True, JobDB.alerted == False)
                .order_by(JobDB.scraped_at.desc())
                .limit(limit)
            )
            return list(result.scalars().all())
    
    async def mark_jobs_alerted(
        self, job_ids: list[str], channels: list[str]
    ) -> None:
        async with self.session() as session:
            for job_id in job_ids:
                db_job = await session.get(JobDB, job_id)
                if db_job:
                    db_job.alerted = True
                    db_job.alerted_at = datetime.utcnow()
                    db_job.alerted_channels = list(set(db_job.alerted_channels + channels))
                    db_job.is_new = False
    
    # Seen jobs (deduplication)
    async def is_job_seen(self, company_id: str, external_id: str) -> bool:
        async with self.session() as session:
            seen_id = f"{company_id}:{external_id}"
            result = await session.get(SeenJobDB, seen_id)
            return result is not None
    
    async def mark_job_seen(
        self, company_id: str, external_id: str, title: str, url: str
    ) -> SeenJobDB:
        async with self.session() as session:
            seen_id = f"{company_id}:{external_id}"
            seen = await session.get(SeenJobDB, seen_id)
            if seen:
                seen.last_seen = datetime.utcnow()
            else:
                seen = SeenJobDB(
                    id=seen_id,
                    company_id=company_id,
                    external_id=external_id,
                    job_title=title,
                    job_url=url,
                )
                session.add(seen)
            await session.flush()
            return seen
    
    async def increment_alert_count(
        self, company_id: str, external_id: str, channels: list[str]
    ) -> None:
        async with self.session() as session:
            seen_id = f"{company_id}:{external_id}"
            seen = await session.get(SeenJobDB, seen_id)
            if seen:
                seen.alert_count += 1
                seen.last_alerted = datetime.utcnow()
                seen.alerted_channels = list(set(seen.alerted_channels + channels))
    
    # Alert logging
    async def log_alert(
        self, job_id: str, channel: str, recipient: Optional[str],
        status: str, error: Optional[str] = None
    ) -> AlertLogDB:
        async with self.session() as session:
            log = AlertLogDB(
                job_id=job_id,
                channel=channel,
                recipient=recipient,
                status=status,
                error_message=error,
            )
            session.add(log)
            await session.flush()
            return log
    
    # User companies
    async def add_user_company(self, company: Company) -> UserCompanyDB:
        async with self.session() as session:
            data = company.model_dump()
            data['career_url'] = str(company.career_url)
            db_company = UserCompanyDB(**data)
            session.add(db_company)
            await session.flush()
            return db_company
    
    async def get_user_companies(self) -> list[UserCompanyDB]:
        async with self.session() as session:
            result = await session.execute(
                select(UserCompanyDB)
                .where(UserCompanyDB.enabled == True)
                .order_by(UserCompanyDB.priority)
            )
            return list(result.scalars().all())
    
    async def remove_user_company(self, company_id: str) -> bool:
        async with self.session() as session:
            db_company = await session.get(UserCompanyDB, company_id)
            if db_company:
                await session.delete(db_company)
                return True
            return False


# Global instance
_db_manager: Optional[DatabaseManager] = None


def get_db_manager(database_url: Optional[str] = None) -> DatabaseManager:
    """Get or create database manager singleton"""
    global _db_manager
    if _db_manager is None:
        if database_url is None:
            database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///data/job_radar.db")
        _db_manager = DatabaseManager(database_url)
    return _db_manager


async def init_database(database_url: Optional[str] = None) -> DatabaseManager:
    """Initialize database and return manager"""
    manager = get_db_manager(database_url)
    await manager.init_db()
    return manager