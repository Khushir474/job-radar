"""Job Radar - Storage Operations"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from job_radar.database import DatabaseManager, get_db_manager
from job_radar.models import Company, Job


class CompanyStorage:
    """Company storage operations"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    async def save_company(self, company: Company) -> None:
        await self.db.upsert_company(company)
    
    async def get_company(self, company_id: str) -> Optional[Company]:
        db_company = await self.db.get_company(company_id)
        if db_company:
            return Company(
                id=db_company.id,
                name=db_company.name,
                career_url=db_company.career_url,
                ats_type=db_company.ats_type,
                ats_config=db_company.ats_config,
                search_keywords=db_company.search_keywords,
                enabled=db_company.enabled,
                priority=db_company.priority,
                custom_scraper=db_company.custom_scraper,
                created_at=db_company.created_at,
                updated_at=db_company.updated_at,
                last_scraped=db_company.last_scraped,
                last_scrape_status=db_company.last_scrape_status,
                jobs_found_total=db_company.jobs_found_total,
            )
        return None
    
    async def get_enabled_companies(self) -> list[Company]:
        db_companies = await self.db.get_enabled_companies()
        return [
            Company(
                id=c.id,
                name=c.name,
                career_url=c.career_url,
                ats_type=c.ats_type,
                ats_config=c.ats_config,
                search_keywords=c.search_keywords,
                enabled=c.enabled,
                priority=c.priority,
                custom_scraper=c.custom_scraper,
                created_at=c.created_at,
                updated_at=c.updated_at,
                last_scraped=c.last_scraped,
                last_scrape_status=c.last_scrape_status,
                jobs_found_total=c.jobs_found_total,
            )
            for c in db_companies
        ]
    
    async def update_scrape_status(self, company_id: str, status: str, jobs_found: int = 0) -> None:
        await self.db.update_company_scrape_status(company_id, status, jobs_found)


class JobStorage:
    """Job storage operations"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    async def save_job(self, job: Job) -> Job:
        db_job = await self.db.upsert_job(job)
        return Job(
            id=db_job.id,
            company_id=db_job.company_id,
            external_id=db_job.external_id,
            title=db_job.title,
            url=db_job.url,
            location=db_job.location,
            department=db_job.department,
            experience_level=db_job.experience_level,
            job_type=db_job.job_type,
            posted_date=db_job.posted_date,
            description=db_job.description,
            raw_data=db_job.raw_data,
            matched_roles=db_job.matched_roles,
            matched_keywords=db_job.matched_keywords,
            scraped_at=db_job.scraped_at,
            first_seen_at=db_job.first_seen_at,
            last_seen_at=db_job.last_seen_at,
            is_new=db_job.is_new,
            alerted=db_job.alerted,
            alerted_at=db_job.alerted_at,
            alerted_channels=db_job.alerted_channels,
        )
    
    async def get_new_jobs(self, limit: int = 100) -> list[Job]:
        db_jobs = await self.db.get_new_jobs(limit)
        return [
            Job(
                id=j.id,
                company_id=j.company_id,
                external_id=j.external_id,
                title=j.title,
                url=j.url,
                location=j.location,
                department=j.department,
                experience_level=j.experience_level,
                job_type=j.job_type,
                posted_date=j.posted_date,
                description=j.description,
                raw_data=j.raw_data,
                matched_roles=j.matched_roles,
                matched_keywords=j.matched_keywords,
                scraped_at=j.scraped_at,
                first_seen_at=j.first_seen_at,
                last_seen_at=j.last_seen_at,
                is_new=j.is_new,
                alerted=j.alerted,
                alerted_at=j.alerted_at,
                alerted_channels=j.alerted_channels,
            )
            for j in db_jobs
        ]
    
    async def mark_alerted(self, job_ids: list[str], channels: list[str]) -> None:
        await self.db.mark_jobs_alerted(job_ids, channels)


class SeenJobStorage:
    """Seen job tracking for deduplication"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    async def is_seen(self, company_id: str, external_id: str) -> bool:
        return await self.db.is_job_seen(company_id, external_id)
    
    async def mark_seen(self, company_id: str, external_id: str, title: str, url: str) -> None:
        await self.db.mark_job_seen(company_id, external_id, title, url)
    
    async def increment_alerts(self, company_id: str, external_id: str, channels: list[str]) -> None:
        await self.db.increment_alert_count(company_id, external_id, channels)


class AlertLogStorage:
    """Alert delivery logging"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    async def log_delivery(
        self,
        job_id: str,
        channel: str,
        recipient: Optional[str],
        status: str,
        error: Optional[str] = None,
    ) -> None:
        await self.db.log_alert(job_id, channel, recipient, status, error)


class UserCompanyStorage:
    """User-added company storage"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    async def add_company(self, company: Company) -> None:
        await self.db.add_user_company(company)
    
    async def get_companies(self) -> list[Company]:
        db_companies = await self.db.get_user_companies()
        return [
            Company(
                id=c.id,
                name=c.name,
                career_url=c.career_url,
                ats_type=c.ats_type,
                ats_config=c.ats_config,
                search_keywords=c.search_keywords,
                enabled=c.enabled,
                priority=c.priority,
            )
            for c in db_companies
        ]
    
    async def remove_company(self, company_id: str) -> bool:
        return await self.db.remove_user_company(company_id)


# Convenience function to get all storage instances
async def get_storages(database_url: Optional[str] = None) -> tuple:
    """Get all storage instances"""
    db = get_db_manager(database_url)
    await db.init_db()
    
    return (
        CompanyStorage(db),
        JobStorage(db),
        SeenJobStorage(db),
        AlertLogStorage(db),
        UserCompanyStorage(db),
    )