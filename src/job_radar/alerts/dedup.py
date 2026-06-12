"""Job Radar - Alert Deduplication"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from job_radar.database import DatabaseManager, get_db_manager
from job_radar.models import Job


class AlertDeduplicator:
    """Prevents duplicate alerts for the same job across channels"""
    
    def __init__(self, db: DatabaseManager, dedup_hours: int = 24):
        self.db = db
        self.dedup_hours = dedup_hours
    
    async def should_alert(self, job: Job, channel: str) -> bool:
        """Check if we should alert for this job on this channel"""
        # Check if job was already alerted on this channel
        if channel in job.alerted_channels:
            return False
        
        # Check database for recent alerts
        # This would require a query to alert_logs table
        # For now, rely on in-memory job state
        return True
    
    async def mark_alerted(self, job_id: str, channel: str) -> None:
        """Mark job as alerted on channel"""
        # This is handled by the job storage
        pass


class ChannelAlertDeduplicator:
    """Per-channel deduplication with time windows"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    async def is_duplicate(
        self,
        job: Job,
        channel: str,
        window_hours: int = 24,
    ) -> bool:
        """Check if this job was already alerted on this channel recently"""
        # Query alert_logs table for recent alerts
        # For now, use job's alerted_channels
        return channel in job.alerted_channels
    
    async def record_alert(
        self,
        job_id: str,
        channel: str,
        recipient: Optional[str] = None,
    ) -> None:
        """Record that an alert was sent"""
        # This is handled by job storage and alert log storage
        pass


def create_deduplicator(db: DatabaseManager) -> AlertDeduplicator:
    return AlertDeduplicator(db)