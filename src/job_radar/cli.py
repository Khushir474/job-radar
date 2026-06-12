"""Job Radar - Command Line Interface"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from job_radar.config import ConfigManager, Settings
from job_radar.database import init_database, get_db_manager
from job_radar.storage import UserCompanyStorage
from job_radar.models import Company, ATSType
from job_radar.scripts.check_jobs import check_jobs

app = typer.Typer(
    name="job-radar",
    help="🔍 Job Radar - Automated job alert system for AI/ML roles",
    add_completion=False,
)
console = Console()

config_manager = ConfigManager()


@app.command()
def check(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Run job check immediately"""
    if verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    console.print("🔍 Running job check...")
    count = asyncio.run(check_jobs())
    console.print(f"✅ Check complete: {count} new jobs found")


@app.command()
def status():
    """Show system status"""
    config = config_manager.load_config()
    
    console.print("📊 [bold]Job Radar Status[/bold]")
    console.print(f"  Database: {config.database_url}")
    console.print(f"  Companies: {len(config.companies)} configured")
    console.print(f"  Check interval: {config.scheduler.check_interval_hours} hours")
    console.print(f"  Quiet hours: {config.scheduler.quiet_hours_start} - {config.scheduler.quiet_hours_end} ({config.scheduler.timezone})")
    
    # Alert channels
    table = Table(title="Alert Channels")
    table.add_column("Channel")
    table.add_column("Enabled")
    table.add_column("Configured")
    
    alerts = config.alerts
    channels = [
        ("iMessage", alerts.imessage_enabled, bool(alerts.imessage_recipients)),
        ("Telegram", alerts.telegram_enabled, bool(alerts.telegram_bot_token and alerts.telegram_chat_ids)),
        ("Discord", alerts.discord_enabled, bool(alerts.discord_webhook_url)),
        ("Email", alerts.email_enabled, bool(alerts.email_smtp_host and alerts.email_username)),
        ("File", alerts.file_enabled, True),
    ]
    
    for name, enabled, configured in channels:
        status = "✅" if enabled and configured else "⚠️" if enabled else "❌"
        table.add_row(name, status + " " + ("Yes" if enabled else "No"), "Yes" if configured else "No")
    
    console.print(table)


@app.command()
def companies(
    list: bool = typer.Option(False, "--list", "-l", help="List all companies"),
    add: bool = typer.Option(False, "--add", "-a", help="Add a new company"),
    remove: Optional[str] = typer.Option(None, "--remove", "-r", help="Remove company by ID"),
    show: Optional[str] = typer.Option(None, "--show", "-s", help="Show company details"),
):
    """Manage companies"""
    config = config_manager.load_config()
    
    if list:
        table = Table(title=f"Companies ({len(config.companies)} total)")
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("ATS")
        table.add_column("Enabled")
        table.add_column("Priority")
        
        for c in config.companies:
            table.add_row(
                c.id, c.name, c.ats_type.value,
                "✅" if c.enabled else "❌",
                str(c.priority)
            )
        console.print(table)
    
    elif add:
        console.print("📝 Add new company (interactive)")
        company_id = typer.prompt("Company ID (slug)")
        name = typer.prompt("Company name")
        career_url = typer.prompt("Career page URL")
        
        ats_options = [ats.value for ats in ATSType]
        ats_type = typer.prompt("ATS type", default="custom")
        
        # Validate ATS type
        if ats_type not in ats_options:
            console.print(f"❌ Invalid ATS type. Options: {', '.join(ats_options)}")
            return
        
        ats_type_enum = ATSType(ats_type)
        
        # ATS-specific config
        ats_config = {}
        if ats_type == "greenhouse":
            ats_config["board_token"] = typer.prompt("Greenhouse board token")
        elif ats_type == "lever":
            ats_config["board_token"] = typer.prompt("Lever board token")
        elif ats_type == "workday":
            ats_config["tenant"] = typer.prompt("Workday tenant")
            ats_config["career_site"] = typer.prompt("Career site name", default="external")
        
        keywords = typer.prompt("Search keywords (comma-separated)", default="")
        priority = typer.prompt("Priority (1=highest)", type=int, default=10)
        
        company = Company(
            id=company_id,
            name=name,
            career_url=career_url,
            ats_type=ATSType(ats_type),
            ats_config=ats_config,
            search_keywords=[k.strip() for k in keywords.split(",") if k.strip()],
            priority=priority,
        )
        
        config_manager.save_user_company(company)
        console.print(f"✅ Added {name} ({company_id})")
    
    elif remove:
        if config_manager.remove_user_company(remove):
            console.print(f"✅ Removed company: {remove}")
        else:
            console.print(f"❌ Company not found: {remove}")
    
    elif show:
        company = next((c for c in config.companies if c.id == show), None)
        if company:
            console.print(f"[bold]{company.name}[/bold] ({company.id})")
            console.print(f"  URL: {company.career_url}")
            console.print(f"  ATS: {company.ats_type.value}")
            console.print(f"  Config: {company.ats_config}")
            console.print(f"  Keywords: {company.search_keywords}")
            console.print(f"  Enabled: {company.enabled}")
            console.print(f"  Priority: {company.priority}")
        else:
            console.print(f"❌ Company not found: {show}")
    
    else:
        console.print("Use --list, --add, --remove, or --show")


@app.command()
def test_alerts(
    channel: Optional[str] = typer.Option(None, "--channel", "-c", help="Specific channel to test"),
):
    """Send test alerts to verify configuration"""
    from job_radar.alerts import AlertManager
    
    config = config_manager.load_config()
    alert_manager = AlertManager(config.alerts)
    
    if channel:
        console.print(f"🧪 Testing {channel}...")
        results = asyncio.run(alert_manager.send_test_alerts([channel]))
    else:
        console.print("🧪 Testing all enabled channels...")
        results = asyncio.run(alert_manager.test_all_channels())
    
    table = Table(title="Test Results")
    table.add_column("Channel")
    table.add_column("Status")
    table.add_column("Details")
    
    for ch, (success, msg) in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        table.add_row(ch, status, msg or "OK")
    
    console.print(table)


@app.command()
def init_db():
    """Initialize database"""
    config = config_manager.load_config()
    console.print("🔧 Initializing database...")
    
    async def _init():
        db = await init_database(config.database_url)
        
        # Save built-in companies
        from job_radar.config import BUILTIN_COMPANIES
        from job_radar.storage import UserCompanyStorage
        company_storage = UserCompanyStorage(db)
        for company in BUILTIN_COMPANIES:
            await company_storage.add_company(company)
        await db.close()
    
    asyncio.run(_init())
    console.print("✅ Database initialized with built-in companies")


@app.command()
def config_show():
    """Show current configuration"""
    config = config_manager.load_config()
    
    import yaml
    console.print(yaml.dump(config.model_dump(), default_flow_style=False, sort_keys=False))


@app.command()
def config_example():
    """Generate example configuration"""
    from job_radar.config import create_example_config
    example = create_example_config()
    console.print(example)


@app.command()
def version():
    """Show version"""
    from job_radar import __version__
    console.print(f"Job Radar v{__version__}")


@app.callback()
def callback():
    """
    Job Radar - Automated job alert system for AI/ML roles
    
    Tracks DA/DS/ML/AI positions at 30+ top AI companies
    and sends alerts via iMessage, Telegram, Discord, Email, and File.
    """
    pass


if __name__ == "__main__":
    app()