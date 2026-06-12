"""Job Radar - iMessage Alert Channel"""

from __future__ import annotations

import subprocess
from typing import Optional

from job_radar.alerts.formatter import BaseAlertChannel
from job_radar.models import Job, AlertConfig


class IMessageChannel(BaseAlertChannel):
    """iMessage alert channel using imsg CLI"""
    
    @property
    def channel_name(self) -> str:
        return "imessage"
    
    @property
    def is_enabled(self) -> bool:
        return self.config.imessage_enabled and len(self.config.imessage_recipients) > 0
    
    async def send(self, jobs: list[Job], recipient: Optional[str] = None) -> tuple[bool, Optional[str]]:
        if not self.is_enabled:
            return False, "Channel not enabled"
        
        recipients = [recipient] if recipient else self.config.imessage_recipients
        message = self.format_jobs_message(jobs)
        
        all_success = True
        last_error = None
        
        for recipient in recipients:
            try:
                # Use imsg CLI to send iMessage
                result = subprocess.run(
                    ["imsg", "send", recipient, message],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode != 0:
                    all_success = False
                    last_error = f"imsg failed for {recipient}: {result.stderr}"
            except FileNotFoundError:
                return False, "imsg CLI not found. Install with: brew install imessage-mcp"
            except subprocess.TimeoutExpired:
                all_success = False
                last_error = f"Timeout sending to {recipient}"
            except Exception as e:
                all_success = False
                last_error = f"Error sending to {recipient}: {str(e)}"
        
        return all_success, last_error


class MacOSMessagesChannel(BaseAlertChannel):
    """Alternative: Use AppleScript to send via Messages app"""
    
    @property
    def channel_name(self) -> str:
        return "imessage"
    
    @property
    def is_enabled(self) -> bool:
        return self.config.imessage_enabled and len(self.config.imessage_recipients) > 0
    
    async def send(self, jobs: list[Job], recipient: Optional[str] = None) -> tuple[bool, Optional[str]]:
        if not self.is_enabled:
            return False, "Channel not enabled"
        
        recipients = [recipient] if recipient else self.config.imessage_recipients
        message = self.format_jobs_message(jobs)
        
        all_success = True
        last_error = None
        
        for recipient in recipients:
            try:
                # Escape quotes for AppleScript
                escaped_message = message.replace('"', '\\"').replace('\n', '\\n')
                escaped_recipient = recipient.replace('"', '\\"')
                
                script = f'''
                tell application "Messages"
                    set targetService to 1st service whose service type = iMessage
                    set targetBuddy to buddy "{escaped_recipient}" of targetService
                    send "{escaped_message}" to targetBuddy
                end tell
                '''
                
                result = subprocess.run(
                    ["osascript", "-e", script],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode != 0:
                    all_success = False
                    last_error = f"AppleScript failed for {recipient}: {result.stderr}"
            except subprocess.TimeoutExpired:
                all_success = False
                last_error = f"Timeout sending to {recipient}"
            except Exception as e:
                all_success = False
                last_error = f"Error sending to {recipient}: {str(e)}"
        
        return all_success, last_error