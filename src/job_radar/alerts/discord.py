"""Job Radar - Discord Alert Channel"""

from __future__ import annotations

from typing import Optional

import httpx

from job_radar.alerts.formatter import BaseAlertChannel, AlertFormatter
from job_radar.models import Job, AlertConfig


class DiscordChannel(BaseAlertChannel):
    """Discord alert channel using webhooks"""
    
    @property
    def channel_name(self) -> str:
        return "discord"
    
    @property
    def is_enabled(self) -> bool:
        return self.config.discord_enabled and bool(self.config.discord_webhook_url)
    
    async def send(self, jobs: list[Job], recipient: Optional[str] = None) -> tuple[bool, Optional[str]]:
        if not self.is_enabled:
            return False, "Channel not enabled"
        
        # Use custom webhook if provided, otherwise use config
        webhook_url = recipient or self.config.discord_webhook_url
        
        # Format for Discord (uses markdown)
        formatter = AlertFormatter(self.config)
        content = formatter.format_for_channel("discord", jobs)
        
        # Discord has 2000 char limit per message
        if len(content) > 1900:
            content = content[:1900] + "\n... (truncated)"
        
        payload = {
            "content": content,
            "username": "Job Radar",
            "avatar_url": "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
        }
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(webhook_url, json=payload)
                response.raise_for_status()
                return True, None
        except httpx.HTTPStatusError as e:
            return False, f"Discord webhook error: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            return False, f"Error sending to Discord: {str(e)}"
    
    async def test_connection(self) -> tuple[bool, Optional[str]]:
        """Test Discord webhook"""
        if not self.config.discord_webhook_url:
            return False, "No webhook URL configured"
        
        payload = {
            "content": "🔔 Job Radar test message - connection successful!",
            "username": "Job Radar",
        }
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(self.config.discord_webhook_url, json=payload)
                response.raise_for_status()
                return True, "Webhook test successful"
        except Exception as e:
            return False, f"Webhook test failed: {str(e)}"