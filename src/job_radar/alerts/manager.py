"""Job Radar - Alert Manager"""

from __future__ import annotations

import logging
from typing import Optional

from job_radar.alerts.formatter import AlertFormatter
from job_radar.alerts.imessage import MacOSMessagesChannel
from job_radar.alerts.telegram import TelegramChannel
from job_radar.alerts.discord import DiscordChannel
from job_radar.alerts.email import EmailChannel
from job_radar.alerts.file_logger import FileLoggerChannel
from job_radar.models import Job, AlertConfig

logger = logging.getLogger(__name__)


class AlertManager:
    """Manages all alert channels and coordinates delivery"""
    
    def __init__(self, config: AlertConfig):
        self.config = config
        self.formatter = AlertFormatter(config)
        self.channels = {
            "imessage": MacOSMessagesChannel(config),
            "telegram": TelegramChannel(config),
            "discord": DiscordChannel(config),
            "email": EmailChannel(config),
            "file": FileLoggerChannel(config),
        }
        self.enabled_channels = [
            name for name, channel in self.channels.items()
            if channel.is_enabled
        ]
    
    async def send_alerts(
        self,
        jobs: list[Job],
        channels: Optional[list[str]] = None,
    ) -> dict[str, tuple[bool, Optional[str]]]:
        """Send alerts for jobs to specified channels"""
        if not jobs:
            return {}
        
        target_channels = channels or self.enabled_channels
        results = {}
        
        for channel_name in target_channels:
            channel = self.channels.get(channel_name)
            if not channel:
                results[channel_name] = (False, f"Unknown channel: {channel_name}")
                continue
            
            if not channel.is_enabled:
                results[channel_name] = (False, f"Channel {channel_name} not enabled")
                continue
            
            try:
                logger.info(f"Sending {len(jobs)} jobs to {channel_name}")
                success, error = await channel.send(jobs)
                results[channel_name] = (success, error)
                
                if success:
                    logger.info(f"Successfully sent to {channel_name}")
                else:
                    logger.error(f"Failed to send to {channel_name}: {error}")
            except Exception as e:
                logger.error(f"Exception sending to {channel_name}: {e}")
                results[channel_name] = (False, str(e))
        
        return results
    
    async def send_test_alerts(self, channels: Optional[list[str]] = None) -> dict[str, tuple[bool, Optional[str]]]:
        """Send test alerts to verify channel configuration"""
        from job_radar.models import RoleCategory
        from datetime import datetime
        
        # Create test job
        test_job = Job(
            id="test:test-job",
            company_id="test",
            external_id="test-job",
            title="Test Job Alert (Test Message)",
            url="https://example.com/job/test",
            location="Remote",
            department="Engineering",
            experience_level=None,
            matched_roles=[RoleCategory.ML_ENGINEER],
            matched_keywords=["machine learning", "python"],
            description="This is a test message from Job Radar to verify alert channel configuration.",
        )
        
        return await self.send_alerts([test_job], channels)
    
    def get_channel_status(self) -> dict[str, dict]:
        """Get status of all channels"""
        return {
            name: {
                "enabled": channel.is_enabled,
                "configured": self._is_configured(name),
            }
            for name, channel in self.channels.items()
        }
    
    def _is_configured(self, channel_name: str) -> bool:
        """Check if channel has required configuration"""
        config = self.config
        if channel_name == "imessage":
            return config.imessage_enabled and len(config.imessage_recipients) > 0
        elif channel_name == "telegram":
            return config.telegram_enabled and bool(config.telegram_bot_token) and len(config.telegram_chat_ids) > 0
        elif channel_name == "discord":
            return config.discord_enabled and bool(config.discord_webhook_url)
        elif channel_name == "email":
            return (
                config.email_enabled
                and bool(config.email_smtp_host)
                and bool(config.email_username)
                and bool(config.email_password)
                and len(config.email_recipients) > 0
            )
        elif channel_name == "file":
            return config.file_enabled
        return False
    
    async def test_all_channels(self) -> dict[str, tuple[bool, Optional[str]]]:
        """Test all enabled channels"""
        results = {}
        
        for name, channel in self.channels.items():
            if not channel.is_enabled:
                results[name] = (False, "Not enabled")
                continue
            
            if hasattr(channel, "test_connection"):
                try:
                    results[name] = await channel.test_connection()
                except Exception as e:
                    results[name] = (False, f"Test failed: {e}")
            else:
                # For channels without test, send a test alert
                results[name] = await self.send_test_alerts([name])
        
        return results