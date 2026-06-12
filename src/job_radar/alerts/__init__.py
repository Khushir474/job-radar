"""Job Radar - Alerts Package"""

from job_radar.alerts.formatter import AlertFormatter, BaseAlertChannel
from job_radar.alerts.manager import AlertManager
from job_radar.alerts.imessage import IMessageChannel
from job_radar.alerts.telegram import TelegramChannel
from job_radar.alerts.discord import DiscordChannel
from job_radar.alerts.email import EmailChannel
from job_radar.alerts.file_logger import FileLoggerChannel
from job_radar.alerts.dedup import AlertDeduplicator

__all__ = [
    "AlertFormatter",
    "BaseAlertChannel",
    "AlertManager",
    "IMessageChannel",
    "TelegramChannel",
    "DiscordChannel",
    "EmailChannel",
    "FileLoggerChannel",
    "AlertDeduplicator",
]