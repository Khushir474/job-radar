"""Job Radar - Email Alert Channel"""

from __future__ import annotations

from email.message import EmailMessage
from typing import Optional

import aiosmtplib

from job_radar.alerts.formatter import BaseAlertChannel, AlertFormatter
from job_radar.models import Job, AlertConfig


class EmailChannel(BaseAlertChannel):
    """Email alert channel using SMTP"""
    
    @property
    def channel_name(self) -> str:
        return "email"
    
    @property
    def is_enabled(self) -> bool:
        return (
            self.config.email_enabled
            and bool(self.config.email_smtp_host)
            and bool(self.config.email_username)
            and bool(self.config.email_password)
            and len(self.config.email_recipients) > 0
        )
    
    async def send(self, jobs: list[Job], recipient: Optional[str] = None) -> tuple[bool, Optional[str]]:
        if not self.is_enabled:
            return False, "Channel not enabled"
        
        recipients = [recipient] if recipient else self.config.email_recipients
        formatter = AlertFormatter(self.config)
        
        # Create email message
        subject = f"🚨 Job Radar: {len(jobs)} New Job Alert{'s' if len(jobs) > 1 else ''}"
        html_content = formatter.format_for_channel("email", jobs)
        text_content = formatter.format_for_channel("imessage", jobs)
        
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self.config.email_from or self.config.email_username
        message["To"] = ", ".join(recipients)
        message.set_content(text_content)
        message.add_alternative(html_content, subtype="html")
        
        try:
            use_tls = self.config.email_use_tls and self.config.email_smtp_port == 465
            start_tls = not use_tls and self.config.email_smtp_port == 587
            await aiosmtplib.send(
                message,
                hostname=self.config.email_smtp_host,
                port=self.config.email_smtp_port,
                username=self.config.email_username,
                password=self.config.email_password,
                use_tls=use_tls,
                start_tls=start_tls,
            )
            return True, None
        except aiosmtplib.SMTPAuthenticationError:
            return False, "SMTP authentication failed"
        except aiosmtplib.SMTPConnectError:
            return False, "Could not connect to SMTP server"
        except Exception as e:
            return False, f"Email error: {str(e)}"
    
    async def test_connection(self) -> tuple[bool, Optional[str]]:
        """Test SMTP connection"""
        if not all([self.config.email_smtp_host, self.config.email_username, self.config.email_password]):
            return False, "SMTP credentials not configured"

        try:
            use_tls = self.config.email_use_tls and self.config.email_smtp_port == 465
            start_tls = not use_tls and self.config.email_smtp_port == 587
            await aiosmtplib.connect(
                hostname=self.config.email_smtp_host,
                port=self.config.email_smtp_port,
                username=self.config.email_username,
                password=self.config.email_password,
                use_tls=use_tls,
                start_tls=start_tls,
            )
            return True, "SMTP connection successful"
        except Exception as e:
            return False, f"SMTP test failed: {str(e)}"