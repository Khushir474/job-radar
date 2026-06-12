"""Job Radar - Quiet Hours Scheduler"""

from __future__ import annotations

from datetime import datetime, time
from typing import Optional

import pytz


class QuietHoursChecker:
    """Checks if current time is within quiet hours"""
    
    def __init__(
        self,
        start_time: str = "22:00",  # 10 PM
        end_time: str = "06:00",    # 6 AM
        timezone: str = "America/Los_Angeles",
    ):
        self.start_time = self._parse_time(start_time)
        self.end_time = self._parse_time(end_time)
        self.timezone = pytz.timezone(timezone)
    
    def _parse_time(self, time_str: str) -> time:
        """Parse HH:MM string to time object"""
        hour, minute = map(int, time_str.split(":"))
        return time(hour, minute)
    
    def is_quiet_hours(self, dt: Optional[datetime] = None) -> bool:
        """Check if given datetime is in quiet hours"""
        if dt is None:
            dt = datetime.now(self.timezone)
        elif dt.tzinfo is None:
            dt = self.timezone.localize(dt)
        else:
            dt = dt.astimezone(self.timezone)
        
        current_time = dt.time()
        
        # Handle overnight quiet hours (e.g., 22:00 to 06:00)
        if self.start_time > self.end_time:
            # Quiet hours span midnight
            return current_time >= self.start_time or current_time < self.end_time
        else:
            # Quiet hours within same day
            return self.start_time <= current_time < self.end_time
    
    def next_active_time(self, dt: Optional[datetime] = None) -> datetime:
        """Get the next time when quiet hours end"""
        from datetime import timedelta
        
        if dt is None:
            dt = datetime.now(self.timezone)
        elif dt.tzinfo is None:
            dt = self.timezone.localize(dt)
        else:
            dt = dt.astimezone(self.timezone)
        
        if not self.is_quiet_hours(dt):
            return dt
        
        # We're in quiet hours, find next end time
        if self.start_time > self.end_time:
            # Overnight: ends at end_time today (if before start) or tomorrow
            if dt.time() >= self.start_time:
                # After start time, ends tomorrow at end_time
                next_day = dt.replace(
                    hour=self.end_time.hour,
                    minute=self.end_time.minute,
                    second=0,
                    microsecond=0,
                ) + timedelta(days=1)
            else:
                # Before end time (early morning), ends today at end_time
                next_day = dt.replace(
                    hour=self.end_time.hour,
                    minute=self.end_time.minute,
                    second=0,
                    microsecond=0,
                )
        else:
            # Same day: ends today at end_time
            next_day = dt.replace(
                hour=self.end_time.hour,
                minute=self.end_time.minute,
                second=0,
                microsecond=0,
            )
            if next_day <= dt:
                next_day += timedelta(days=1)
        
        return next_day
    
    def get_status_message(self, dt: Optional[datetime] = None) -> str:
        """Get human-readable status message"""
        if dt is None:
            dt = datetime.now(self.timezone)
        elif dt.tzinfo is None:
            dt = self.timezone.localize(dt)
        else:
            dt = dt.astimezone(self.timezone)
        
        if self.is_quiet_hours(dt):
            next_active = self.next_active_time(dt)
            return (
                f"🌙 Quiet hours active (until {next_active.strftime('%I:%M %p %Z')})"
            )
        else:
            return f"☀️ Active hours (quiet hours: {self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')} {self.timezone})"


def create_quiet_hours_checker(config) -> QuietHoursChecker:
    """Create QuietHoursChecker from scheduler config"""
    return QuietHoursChecker(
        start_time=config.scheduler.quiet_hours_start,
        end_time=config.scheduler.quiet_hours_end,
        timezone=config.scheduler.timezone,
    )