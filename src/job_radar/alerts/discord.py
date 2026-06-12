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

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                # For large batches, send summary + company breakdown
                if len(jobs) > 20:
                    # Send summary message
                    summary = self._format_summary(jobs)
                    payload = {
                        "content": summary,
                        "username": "Job Radar",
                        "avatar_url": "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
                    }
                    response = await client.post(webhook_url, json=payload)
                    response.raise_for_status()

                    # Send company breakdown
                    breakdown = self._format_company_breakdown(jobs)
                    if breakdown:
                        payload = {
                            "content": breakdown,
                            "username": "Job Radar",
                        }
                        response = await client.post(webhook_url, json=payload)
                        response.raise_for_status()
                else:
                    # For small batches, send detailed list
                    formatter = AlertFormatter(self.config)
                    content = formatter.format_for_channel("discord", jobs)

                    # Discord has 2000 char limit per message
                    if len(content) > 1900:
                        content = content[:1900] + "\n... (see file log for full list)"

                    payload = {
                        "content": content,
                        "username": "Job Radar",
                        "avatar_url": "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
                    }
                    response = await client.post(webhook_url, json=payload)
                    response.raise_for_status()

                return True, None
        except httpx.HTTPStatusError as e:
            return False, f"Discord webhook error: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            return False, f"Error sending to Discord: {str(e)}"

    def _format_summary(self, jobs: list[Job]) -> str:
        """Format summary message for large job batches"""
        from collections import Counter
        companies = Counter(j.company_id for j in jobs)

        lines = [
            f"**New Job Alerts: {len(jobs)} positions**",
            f"*{len(companies)} companies | US-based | Updated now*",
            "",
            "**Top Hiring Companies:**",
        ]

        for company, count in companies.most_common(10):
            lines.append(f"• **{company.title()}**: {count} positions")

        if len(companies) > 10:
            remaining = len(companies) - 10
            lines.append(f"• *+{remaining} more companies*")

        lines.extend([
            "",
            "*See file log for complete job list with details*",
        ])

        return "\n".join(lines)

    def _format_company_breakdown(self, jobs: list[Job]) -> str:
        """Format company breakdown message"""
        from collections import Counter
        companies = Counter(j.company_id for j in jobs)

        if len(companies) <= 10:
            return ""

        lines = ["**All Companies:**"]
        sorted_companies = sorted(companies.items(), key=lambda x: x[1], reverse=True)

        for company, count in sorted_companies:
            lines.append(f"• **{company.title()}**: {count}")

        return "\n".join(lines)
    
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