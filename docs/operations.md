# Operations Guide

Daily operations, monitoring, and maintenance procedures for Job Radar.

## Daily Operations

### Morning Check (9 AM)
```bash
# Quick status
job-radar status

# Check recent alerts
job-radar check
```

### Monitoring Checklist
- [ ] All alert channels working (`job-radar test-alerts`)
- [ ] No scraper errors in logs
- [ ] Database size reasonable
- [ ] Disk space available

---

## Log Analysis

### Check Recent Errors
```bash
# Docker
docker compose logs job-radar-cron | grep -i error | tail -20

# Local
grep -i error logs/job_radar.log | tail -20
```

### Check Scraper Status
```bash
# View last scrape status for each company
sqlite3 data/job_radar.db "
SELECT name, last_scraped, last_scrape_status, jobs_found_total 
FROM companies 
ORDER BY priority, name;
"
```

### Alert Delivery Stats
```bash
# Recent alert deliveries
sqlite3 data/job_radar.db "
SELECT channel, status, COUNT(*) as count, MAX(sent_at) as last_sent
FROM alert_logs
WHERE sent_at > date('now', '-7 days')
GROUP BY channel, status
ORDER BY last_sent DESC;
"
```

---

## Database Maintenance

### Weekly (Automated via cron)
```bash
# Vacuum database
sqlite3 data/job_radar.db "VACUUM;"

# Clean old seen jobs (90+ days)
sqlite3 data/job_radar.db "
DELETE FROM seen_jobs 
WHERE first_seen < date('now', '-90 days');
"

# Clean old alert logs (30+ days)
sqlite3 data/job_radar.db "
DELETE FROM alert_logs 
WHERE sent_at < date('now', '-30 days');
"
```

### Monthly
```bash
# Analyze database
sqlite3 data/job_radar.db "ANALYZE;"

# Check table sizes
sqlite3 data/job_radar.db "
SELECT name, sql FROM sqlite_master WHERE type='table';
"
```

---

## Updating Companies

### Add New Company
```bash
# Interactive
job-radar companies --add

# Or edit YAML directly
nano config/user_companies.yaml
```

### Disable Problematic Company
```bash
# Edit config or use CLI
sqlite3 data/job_radar.db "
UPDATE companies SET enabled=0 WHERE id='problematic-company';
"
```

### Update Scraper for Site Changes
1. Check logs for error patterns
2. Modify appropriate scraper in `src/job_radar/scrapers/`
3. Test: `job-radar check`
4. Deploy update

---

## Alert Channel Troubleshooting

### Telegram
```bash
# Test bot
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe"

# Check chat ID
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getUpdates"
```

### Discord
```bash
# Test webhook
curl -X POST "$DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"content": "Test from Job Radar"}'
```

### Email
```bash
# Test SMTP
telnet smtp.gmail.com 587
# Then: EHLO test, AUTH LOGIN, etc.

# Or use Python
python -c "
import aiosmtplib
import asyncio
async def test():
    await aiosmtplib.connect(
        hostname='smtp.gmail.com', port=587,
        username='$EMAIL_USERNAME', password='$EMAIL_PASSWORD',
        start_tls=True
    )
    print('OK')
asyncio.run(test())
"
```

### iMessage (macOS)
```bash
# Test imsg CLI
imsg send "+15551234567" "Test from Job Radar"

# Or AppleScript
osascript -e 'tell app "Messages" to send "Test" to buddy "+15551234567" of service 1'
```

---

## Performance Tuning

### Scraper Concurrency
```yaml
# config/config.yaml
scheduler:
  max_concurrent_scrapers: 5  # Reduce if rate limited
  request_timeout: 30         # Increase for slow sites
  retry_attempts: 3
  retry_delay: 5
```

### Database Indexes
```sql
-- Already created in schema:
-- CREATE INDEX ix_jobs_company_id ON jobs(company_id);
-- CREATE INDEX ix_jobs_is_new_alerted ON jobs(is_new, alerted);
-- CREATE INDEX ix_jobs_scraped_at ON jobs(scraped_at);
-- CREATE INDEX ix_seen_jobs_company ON seen_jobs(company_id);
```

---

## Backup & Recovery

### Backup
```bash
# Full backup
tar -czf job-radar-backup-$(date +%Y%m%d).tar.gz data/ config/

# Database only
sqlite3 data/job_radar.db ".backup data/job_radar_backup.db"
```

### Restore
```bash
# From backup
tar -xzf job-radar-backup-20240115.tar.gz

# Database only
sqlite3 data/job_radar.db ".restore data/job_radar_backup.db"
```

---

## Incident Response

### Scraper Failing for All Companies
1. Check network connectivity
2. Check if sites blocked (Cloudflare, etc.)
3. Check proxy/VPN if needed
4. Increase delays

### Alert Channel Down
1. Test channel manually
2. Check credentials/API limits
3. Fallback to file logger (always works)

### Database Corruption
1. Restore from backup
2. If no backup, rebuild from seen_jobs

---

## Scaling Considerations

### For 50+ Companies
- Increase `max_concurrent_scrapers` to 10
- Consider Redis for deduplication
- Use PostgreSQL instead of SQLite

### For High Frequency (30 min)
- Add caching layer
- Use incremental scraping
- Parallelize with multiple workers

---

## Useful Commands Reference

```bash
# Run check manually
job-radar check

# Test all alerts
job-radar test-alerts

# Test specific channel
job-radar test-alerts -c telegram

# List companies
job-radar companies -l

# Add company
job-radar companies -a

# Show config
job-radar config-show

# Database queries
sqlite3 data/job_radar.db "SELECT * FROM jobs ORDER BY scraped_at DESC LIMIT 10;"
sqlite3 data/job_radar.db "SELECT * FROM alert_logs ORDER BY sent_at DESC LIMIT 10;"

# Docker management
docker compose logs -f job-radar-cron
docker compose restart job-radar-cron
docker compose down && docker compose up -d --build job-radar-cron
```