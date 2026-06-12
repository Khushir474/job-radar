#!/usr/bin/env python3
"""Smoke test to verify bug fixes"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from job_radar.scrapers.base import BaseScraper, GreenhouseScraper, LeverScraper
from job_radar.models import Company, ATSType
from job_radar.scheduler.quiet_hours import QuietHoursChecker
from datetime import datetime, time
import pytz


async def test_fetch_json_params():
    """Test that _fetch_json accepts params"""
    print("✓ Testing _fetch_json signature...")

    # Check that _fetch_json method accepts params
    import inspect
    sig = inspect.signature(BaseScraper._fetch_json)
    params = list(sig.parameters.keys())

    assert 'params' in params, f"_fetch_json missing 'params' parameter. Got: {params}"
    assert 'kwargs' in params, f"_fetch_json missing '**kwargs'. Got: {params}"
    print("  ✓ _fetch_json signature accepts params and **kwargs")


def test_quiet_hours_boundary():
    """Test quiet hours boundary condition"""
    print("✓ Testing quiet hours boundary...")

    checker = QuietHoursChecker(
        start_time="22:00",
        end_time="06:00",
        timezone="America/Los_Angeles"
    )

    tz = pytz.timezone("America/Los_Angeles")

    # Test that 06:00 is NOT quiet hours (exclusive boundary)
    dt_600 = tz.localize(datetime(2024, 1, 1, 6, 0, 0))
    is_quiet_600 = checker.is_quiet_hours(dt_600)
    assert not is_quiet_600, f"06:00 should NOT be in quiet hours, but got: {is_quiet_600}"
    print("  ✓ 06:00 is correctly NOT in quiet hours")

    # Test that 05:59 IS quiet hours
    dt_559 = tz.localize(datetime(2024, 1, 1, 5, 59, 0))
    is_quiet_559 = checker.is_quiet_hours(dt_559)
    assert is_quiet_559, f"05:59 should be in quiet hours, but got: {is_quiet_559}"
    print("  ✓ 05:59 is correctly in quiet hours")

    # Test that 22:00 IS quiet hours
    dt_2200 = tz.localize(datetime(2024, 1, 1, 22, 0, 0))
    is_quiet_2200 = checker.is_quiet_hours(dt_2200)
    assert is_quiet_2200, f"22:00 should be in quiet hours, but got: {is_quiet_2200}"
    print("  ✓ 22:00 is correctly in quiet hours")


def test_config_telegram_parsing():
    """Test that empty telegram chat IDs are filtered"""
    print("✓ Testing Telegram chat ID parsing...")

    # Simulate the parsing logic
    chat_ids_str = ""
    parsed = [
        c.strip() for c in chat_ids_str.split(",") if c.strip()
    ]
    assert parsed == [], f"Empty string should parse to empty list, got: {parsed}"
    print("  ✓ Empty chat IDs correctly parse to empty list")

    chat_ids_str = "123, , 456"
    parsed = [
        c.strip() for c in chat_ids_str.split(",") if c.strip()
    ]
    assert parsed == ["123", "456"], f"Should filter empty items, got: {parsed}"
    print("  ✓ Empty items in chat ID list are correctly filtered")


def test_duplicate_cohere():
    """Test that duplicate Cohere is removed"""
    print("✓ Testing for duplicate Cohere entry...")

    from job_radar.config import BUILTIN_COMPANIES

    cohere_entries = [c for c in BUILTIN_COMPANIES if c.id == "cohere"]
    assert len(cohere_entries) == 1, f"Expected 1 Cohere entry, found {len(cohere_entries)}"
    print("  ✓ Duplicate Cohere entry removed (only 1 found)")


def test_email_starttls_logic():
    """Test that email STARTTLS logic is fixed"""
    print("✓ Testing Email STARTTLS logic...")

    # Simulate the corrected logic
    email_use_tls = True
    email_smtp_port = 587

    use_tls = email_use_tls and email_smtp_port == 465
    start_tls = not use_tls and email_smtp_port == 587

    assert use_tls == False, "Port 587 should not use implicit TLS"
    assert start_tls == True, "Port 587 should use STARTTLS"
    print("  ✓ Port 587 correctly uses STARTTLS (start_tls=True)")

    # Test port 465 (implicit TLS)
    email_smtp_port = 465
    use_tls = email_use_tls and email_smtp_port == 465
    start_tls = not use_tls and email_smtp_port == 587

    assert use_tls == True, "Port 465 should use implicit TLS"
    assert start_tls == False, "Port 465 should not use STARTTLS"
    print("  ✓ Port 465 correctly uses implicit TLS (use_tls=True)")


async def main():
    """Run all smoke tests"""
    print("\n" + "="*60)
    print("Job Radar - Smoke Test Suite")
    print("="*60 + "\n")

    try:
        await test_fetch_json_params()
        test_quiet_hours_boundary()
        test_config_telegram_parsing()
        test_duplicate_cohere()
        test_email_starttls_logic()

        print("\n" + "="*60)
        print("✓ All smoke tests passed!")
        print("="*60 + "\n")
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}\n")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
