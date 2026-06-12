"""Job Radar - Telegram Alert Channel"""

from __future__ import annotations

from typing import Optional

import httpx

from job_radar.alerts.formatter import BaseAlertChannel
from job_radar.models import Job, AlertConfig


class TelegramChannel(BaseAlertChannel):
    """Telegram alert channel using Bot API"""
    
    @property
    def channel_name(self) -> str:
        return "telegram"
    
    @property
    def is_enabled(self) -> bool:
        return self.config.telegram_enabled and bool(self.config.telegram_bot_token) and len(self.config.telegram_chat_ids) > 0
    
    async def send(self, jobs: list[Job], recipient: Optional[str] = None) -> tuple[bool, Optional[str]]:
        if not self.is_enabled:
            return False, "Channel not enabled"
        
        chat_ids = [recipient] if recipient else self.config.telegram_chat_ids
        message = self.format_jobs_message(jobs)
        
        url = f"https://api.telegram.org/bot{self.config.telegram_bot_token}/sendMessage"
        
        all_success = True
        last_error = None
        
        async with httpx.AsyncClient(timeout=30) as client:
            for chat_id in chat_ids:
                try:
                    response = await client.post(url, json={
                        "chat_id": chat_id,
                        "text": message,
                        "parse_mode": "Markdown",
                        "disable_web_page_preview": True,
                    })
                    response.raise_for_status()
                    result = response.json()
                    if not result.get("ok"):
                        all_success = False
                        last_error = f"Telegram API error: {result.get('description')}"
                except httpx.HTTPStatusError as e:
                    all_success = False
                    last_error = f"HTTP error for {chat_id}: {e.response.status_code}"
                except Exception as e:
                    all_success = False
                    last_error = f"Error sending to {chat_id}: {str(e)}"
        
        return all_success, last_error
    
    async def test_connection(self) -> tuple[bool, Optional[str]]:
        """Test Telegram bot connection"""
        if not self.config.telegram_bot_token:
            return False, "No bot token configured"
        
        url = f"https://api.telegram.org/bot{self.config.telegram_bot_token}/getMe"
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
                response.raise_for_status()
                result = response.json()
                if result.get("ok"):
                    bot_info = result.get("result", {})
                    return True, f"Connected as @{bot_info.get('username', 'unknown')}"
                return False, f"API error: {result.get('description')}"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"