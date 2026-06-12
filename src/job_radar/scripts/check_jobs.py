#!/usr/bin/env python3
"""Job Radar - Main Check Job Script

This script is run by Hermes cron every 2 hours to check for new jobs.
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path for local imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from job_radar.config import ConfigManager, Settings
from job_radar.database import init_database, get_db_manager
from job_radar.matcher import create_matcher_from_config
from job_radar.scrapers import get_scraper
from job_radar.storage import (
    CompanyStorage, JobStorage, SeenJobStorage, AlertLogStorage
)
from job_radar.alerts import AlertManager
from job_radar.scheduler import create_quiet_hours_checker
from job_radar.models import Job

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def check_jobs() -> int:
    """Main job checking routine"""
    logger.info("Starting job check...")
    
    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    # Check quiet hours
    quiet_checker = create_quiet_hours_checker(config)
    if quiet_checker.is_quiet_hours():
        logger.info("Quiet hours active, skipping check")
        print(quiet_checker.get_status_message())
        return 0
    
    logger.info(quiet_checker.get_status_message())
    
    # Initialize database
    db = await init_database(config.database_url)
    
    # Initialize storage
    company_storage = CompanyStorage(db)
    job_storage = JobStorage(db)
    seen_storage = SeenJobStorage(db)
    alert_log = AlertLogStorage(db)
    
    # Initialize matcher
    matcher = create_matcher_from_config(config)
    
    # Initialize alert managers (one per webhook)
    alert_manager = AlertManager(config.alerts)  # Default webhook

    # Get enabled companies (from both lists if they exist)
    companies = await company_storage.get_enabled_companies()
    logger.info(f"Checking {len(companies)} companies...")
    
    all_new_jobs = []
    total_scraped = 0
    total_matched = 0
    
    # Scrape each company
    for company in companies:
        try:
            logger.info(f"Scraping {company.name}...")
            
            scraper = get_scraper(
                company.ats_type,
                company,
                timeout=config.scheduler.request_timeout,
                max_retries=config.scheduler.retry_attempts,
                retry_delay=config.scheduler.retry_delay,
            )
            
            async with scraper:
                scraped_jobs = await scraper.scrape_jobs()
            
            total_scraped += len(scraped_jobs)
            logger.info(f"  Found {len(scraped_jobs)} jobs from {company.name}")
            
            # Update company scrape status
            await company_storage.update_scrape_status(company.id, "success", len(scraped_jobs))
            
            # Process each job
            for scraped in scraped_jobs:
                job = scraper.normalize_job(scraped)
                
                # Check if already seen
                if await seen_storage.is_seen(company.id, job.external_id):
                    continue
                
                # Match against filters
                match_result = matcher.match(job)
                if not match_result.matched:
                    continue
                
                # Update job with match info
                job.matched_roles = match_result.matched_roles
                job.matched_keywords = match_result.matched_keywords
                
                # Save job
                await job_storage.save_job(job)
                await seen_storage.mark_seen(company.id, job.external_id, job.title, str(job.url))
                
                all_new_jobs.append(job)
                total_matched += 1
                
        except Exception as e:
            logger.error(f"Error scraping {company.name}: {e}")
            await company_storage.update_scrape_status(company.id, f"error: {str(e)}")
    
    logger.info(f"Total scraped: {total_scraped}, Matched: {total_matched}, New: {len(all_new_jobs)}")

    # Send alerts for new jobs (group by company webhook if available)
    success_channels = []
    if all_new_jobs:
        logger.info(f"Sending alerts for {len(all_new_jobs)} new jobs...")

        # Group jobs by their company's webhook (if specified)
        jobs_by_webhook = {}
        for job in all_new_jobs:
            company = next((c for c in companies if c.id == job.company_id), None)
            if company and hasattr(company, 'webhook') and company.webhook:
                webhook_url = company.webhook
                if webhook_url not in jobs_by_webhook:
                    jobs_by_webhook[webhook_url] = []
                jobs_by_webhook[webhook_url].append(job)
            else:
                # Use default webhook
                if None not in jobs_by_webhook:
                    jobs_by_webhook[None] = []
                jobs_by_webhook[None].append(job)

        # Send to each webhook
        all_results = {}
        for webhook_url, jobs in jobs_by_webhook.items():
            if webhook_url:
                # Create temporary alert config with custom webhook
                custom_config = config.alerts.model_copy()
                custom_config.discord_webhook_url = webhook_url
                custom_alert_manager = AlertManager(custom_config)
                logger.info(f"Sending {len(jobs)} jobs to custom webhook...")
                results = await custom_alert_manager.send_alerts(jobs)
            else:
                # Use default alert manager
                results = await alert_manager.send_alerts(jobs)

            all_results.update(results)

        # Track which channels succeeded
        success_channels = [ch for ch, (ok, _) in all_results.items() if ok]
        
        if success_channels:
            job_ids = [job.id for job in all_new_jobs]
            await job_storage.mark_alerted(job_ids, success_channels)

            for job in all_new_jobs:
                await seen_storage.increment_alerts(job.company_id, job.external_id, success_channels)

            # Log alert deliveries
            for job in all_new_jobs:
                for channel in success_channels:
                    await alert_log.log_delivery(job.id, channel, None, "sent")

        # Log failures
        for channel, (success, error) in all_results.items():
            if not success:
                for job in all_new_jobs:
                    await alert_log.log_delivery(job.id, channel, None, "failed", error)

        logger.info(f"Alert results: {all_results}")
    else:
        logger.info("No new matching jobs found")
    
    await db.close()
    
    print(f"Check complete: {len(all_new_jobs)} new jobs, alerts sent to {len(success_channels) if all_new_jobs else 0} channels")
    return len(all_new_jobs)


async def main():
    """Entry point"""
    try:
        count = await check_jobs()
        return 0
    except Exception as e:
        logger.exception(f"Job check failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))