"""Job Radar - Alert Formatters and Base Classes"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from job_radar.models import Job, AlertConfig


class BaseAlertChannel(ABC):
    """Base class for alert channels"""
    
    def __init__(self, config: AlertConfig):
        self.config = config
    
    @property
    @abstractmethod
    def channel_name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def is_enabled(self) -> bool:
        pass
    
    @abstractmethod
    async def send(self, jobs: list[Job], recipient: Optional[str] = None) -> tuple[bool, Optional[str]]:
        """Send alert for jobs. Returns (success, error_message)"""
        pass
    
    def format_job(self, job: Job, include_description: bool = True) -> str:
        """Format a single job for alert"""
        lines = [
            f"🏢 **{job.company_id.upper()}** - {job.title}",
            f"📍 {job.location}" if job.location else "",
            f"🔗 {job.url}",
        ]
        
        if job.department:
            lines.append(f"📂 {job.department}")
        if job.experience_level:
            lines.append(f"📊 {job.experience_level.value.replace('_', ' ').title()}")
        if job.matched_roles:
            roles = ", ".join([r.value.replace('_', ' ').title() for r in job.matched_roles])
            lines.append(f"🎯 Roles: {roles}")
        if job.matched_keywords:
            lines.append(f"🔑 Keywords: {', '.join(job.matched_keywords[:5])}")
        
        if include_description and job.description:
            desc = job.description[:500] + "..." if len(job.description) > 500 else job.description
            lines.append(f"\n📝 {desc}")
        
        return "\n".join(filter(None, lines))
    
    def format_jobs_message(self, jobs: list[Job], title: str = "New Job Alerts") -> str:
        """Format multiple jobs into a message"""
        if not jobs:
            return f"{title}\n\nNo new jobs found."
        
        lines = [f"🚨 **{title}** ({len(jobs)} new job{'s' if len(jobs) > 1 else ''})", ""]
        
        for i, job in enumerate(jobs, 1):
            lines.append(f"**{i}.** {self.format_job(job, self.config.include_description)}")
            if i < len(jobs):
                lines.append("---")
        
        lines.append(f"\n⏰ Checked at {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
        return "\n".join(lines)


class AlertFormatter:
    """Formats alerts for different channels"""
    
    def __init__(self, config: AlertConfig):
        self.config = config
    
    def format_for_channel(self, channel: str, jobs: list[Job]) -> str:
        """Format jobs for specific channel"""
        if channel in ["telegram", "discord"]:
            return self._format_markdown(jobs)
        elif channel == "email":
            return self._format_html(jobs)
        elif channel == "imessage":
            return self._format_plain(jobs)
        else:
            return self._format_plain(jobs)
    
    def _format_markdown(self, jobs: list[Job]) -> str:
        if not jobs:
            return "No new jobs found."

        lines = [f"**New Jobs: {len(jobs)} position{'s' if len(jobs) > 1 else ''}**", ""]

        for i, job in enumerate(jobs, 1):
            lines.append(f"{i}. {self._format_single_job(job)}")
            if i < len(jobs):
                lines.append("")

        return "\n".join(lines)
    
    def _format_single_job(self, job: Job) -> str:
        lines = [
            f"**{job.company_id.upper()}**",
            f"*{job.title}*",
        ]

        if job.location:
            lines.append(f"Location: {job.location}")

        if job.experience_level:
            exp = job.experience_level.value.replace('_', ' ').title()
            lines.append(f"Level: {exp}")

        lines.append(f"{job.url}")

        return "\n".join(filter(None, lines))
    
    def _format_html(self, jobs: list[Job]) -> str:
        if not jobs:
            return "<p>No new jobs found.</p>"
        
        lines = [
            "<html><body>",
            f"<h2>🚨 New Job Alerts ({len(jobs)} jobs)</h2>",
            "<hr>",
        ]
        
        for i, job in enumerate(jobs, 1):
            lines.append(f"<h3>{i}. {job.title}</h3>")
            lines.append(f"<p><strong>Company:</strong> {job.company_id.upper()}</p>")
            if job.location:
                lines.append(f"<p><strong>Location:</strong> {job.location}</p>")
            lines.append(f"<p><strong>Link:</strong> <a href='{job.url}'>{job.url}</a></p>")
            if job.department:
                lines.append(f"<p><strong>Department:</strong> {job.department}</p>")
            if job.experience_level:
                lines.append(f"<p><strong>Experience:</strong> {job.experience_level.value.replace('_', ' ').title()}</p>")
            if job.matched_roles:
                roles = ", ".join([r.value.replace('_', ' ').title() for r in job.matched_roles])
                lines.append(f"<p><strong>Matched Roles:</strong> {roles}</p>")
            if job.matched_keywords:
                lines.append(f"<p><strong>Keywords:</strong> {', '.join(job.matched_keywords[:5])}</p>")
            if self.config.include_description and job.description:
                desc = job.description[:500] + "..." if len(job.description) > 500 else job.description
                lines.append(f"<p><strong>Description:</strong></p><p>{desc}</p>")
            lines.append("<hr>")
        
        lines.append(f"<p><em>Checked at {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</em></p>")
        lines.append("</body></html>")
        return "\n".join(lines)
    
    def _format_plain(self, jobs: list[Job]) -> str:
        if not jobs:
            return "No new jobs found."
        
        lines = [f"NEW JOB ALERTS ({len(jobs)} jobs)", "=" * 50, ""]
        
        for i, job in enumerate(jobs, 1):
            lines.append(f"{i}. {job.title}")
            lines.append(f"   Company: {job.company_id.upper()}")
            if job.location:
                lines.append(f"   Location: {job.location}")
            lines.append(f"   URL: {job.url}")
            if job.department:
                lines.append(f"   Department: {job.department}")
            if job.experience_level:
                lines.append(f"   Experience: {job.experience_level.value.replace('_', ' ').title()}")
            if job.matched_roles:
                roles = ", ".join([r.value.replace('_', ' ').title() for r in job.matched_roles])
                lines.append(f"   Matched Roles: {roles}")
            if job.matched_keywords:
                lines.append(f"   Keywords: {', '.join(job.matched_keywords[:5])}")
            if self.config.include_description and job.description:
                desc = job.description[:500] + "..." if len(job.description) > 500 else job.description
                lines.append(f"   Description: {desc}")
            lines.append("")
        
        lines.append(f"Checked at {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
        return "\n".join(lines)
    
    def format_json(self, jobs: list[Job]) -> str:
        """Format as JSON for file logging"""
        import json
        return json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "count": len(jobs),
            "jobs": [
                {
                    "id": job.id,
                    "company_id": job.company_id,
                    "title": job.title,
                    "url": str(job.url),
                    "location": job.location,
                    "department": job.department,
                    "experience_level": job.experience_level.value if job.experience_level else None,
                    "matched_roles": [r.value for r in job.matched_roles],
                    "matched_keywords": job.matched_keywords,
                    "scraped_at": job.scraped_at.isoformat(),
                }
                for job in jobs
            ],
        }, indent=2)