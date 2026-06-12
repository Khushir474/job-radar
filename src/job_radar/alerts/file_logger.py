"""Job Radar - File Logger Alert Channel"""

from __future__ import annotations

import aiofiles
import json
from pathlib import Path
from typing import Optional

from job_radar.alerts.formatter import BaseAlertChannel, AlertFormatter
from job_radar.models import Job, AlertConfig


class FileLoggerChannel(BaseAlertChannel):
    """File logger alert channel"""
    
    @property
    def channel_name(self) -> str:
        return "file"
    
    @property
    def is_enabled(self) -> bool:
        return self.config.file_enabled
    
    async def send(self, jobs: list[Job], recipient: Optional[str] = None) -> tuple[bool, Optional[str]]:
        if not self.is_enabled:
            return False, "Channel not enabled"
        
        file_path = Path(recipient or self.config.file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if self.config.file_format == "json":
                content = AlertFormatter(self.config).format_json(jobs)
                # Append to JSON Lines format
                async with aiofiles.open(file_path, "a") as f:
                    for line in content.split('\n'):
                        if line.strip():
                            await f.write(line + '\n')
            elif self.config.file_format == "markdown":
                content = AlertFormatter(self.config).format_for_channel("telegram", jobs)
                async with aiofiles.open(file_path, "a") as f:
                    await f.write(content + '\n\n---\n\n')
            else:  # plain text
                content = AlertFormatter(self.config).format_for_channel("imessage", jobs)
                async with aiofiles.open(file_path, "a") as f:
                    await f.write(content + '\n\n' + '='*50 + '\n\n')
            
            return True, None
        except Exception as e:
            return False, f"File write error: {str(e)}"
    
    async def read_recent(self, limit: int = 10) -> list[dict]:
        """Read recent alerts from JSON log"""
        file_path = Path(self.config.file_path)
        if not file_path.exists():
            return []
        
        alerts = []
        try:
            async with aiofiles.open(file_path, "r") as f:
                async for line in f:
                    line = line.strip()
                    if line:
                        try:
                            alerts.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
        except Exception:
            pass
        
        return alerts[-limit:]
    
    async def get_stats(self) -> dict:
        """Get log statistics"""
        file_path = Path(self.config.file_path)
        if not file_path.exists():
            return {"total_alerts": 0, "total_jobs": 0, "file_size": 0}
        
        total_alerts = 0
        total_jobs = 0
        
        try:
            async with aiofiles.open(file_path, "r") as f:
                async for line in f:
                    line = line.strip()
                    if line:
                        try:
                            data = json.loads(line)
                            total_alerts += 1
                            total_jobs += data.get("count", 0)
                        except json.JSONDecodeError:
                            pass
        except Exception:
            pass
        
        return {
            "total_alerts": total_alerts,
            "total_jobs": total_jobs,
            "file_size": file_path.stat().st_size,
        }