# Job Radar Filter Configuration for Khushi

**Experience Level:** 2-3 years
**Target Roles:** Internship, Entry-level, Associate, Sr Associate
**Locations:** USA only (states, cities, remote)

---

## ✅ JOBS THAT WILL BE ALERTED

### Role Titles That Match

#### Data Analyst Track
- ✅ Data Analyst
- ✅ Associate Data Analyst
- ✅ Sr Associate Data Analyst
- ✅ Junior Data Analyst
- ✅ Data Analyst (Entry Level)
- ✅ Analytics Analyst
- ✅ BI Analyst
- ✅ SQL Analyst
- ✅ Analytics Engineer

#### Data Scientist Track
- ✅ Data Scientist
- ✅ Associate Data Scientist
- ✅ Sr Associate Data Scientist
- ✅ Junior Data Scientist
- ✅ Data Scientist Intern
- ✅ Machine Learning Scientist
- ✅ ML Scientist

#### ML Engineer Track
- ✅ Machine Learning Engineer
- ✅ ML Engineer
- ✅ Associate ML Engineer
- ✅ Sr Associate ML Engineer
- ✅ Junior ML Engineer
- ✅ ML Engineer Intern
- ✅ ML Ops Engineer
- ✅ MLOps

#### AI Engineer Track
- ✅ AI Engineer
- ✅ Associate AI Engineer
- ✅ Sr Associate AI Engineer
- ✅ Junior AI Engineer
- ✅ AI Engineer Intern
- ✅ LLM Engineer
- ✅ Generative AI Engineer
- ✅ Prompt Engineer
- ✅ RAG Engineer

#### Applied Scientist Track
- ✅ Applied Scientist
- ✅ Associate Applied Scientist
- ✅ Junior Applied Scientist
- ✅ ML Scientist
- ✅ AI Scientist

#### Data Engineer Track
- ✅ Data Engineer
- ✅ Associate Data Engineer
- ✅ Sr Associate Data Engineer
- ✅ Junior Data Engineer
- ✅ Data Engineer Intern
- ✅ ETL Engineer
- ✅ Data Pipeline Engineer
- ✅ Analytics Engineer

#### Research Scientist Track
- ✅ Research Scientist
- ✅ Junior Research Scientist
- ✅ AI Researcher
- ✅ ML Researcher

### Locations That Match

#### Universal
- ✅ Remote
- ✅ Anywhere in United States
- ✅ USA

#### All 50 US States (Full names + abbreviations)
- ✅ California (CA)
- ✅ New York (NY)
- ✅ Texas (TX)
- ✅ Massachusetts (MA)
- ✅ Washington (WA)
- ✅ Colorado (CO)
- ✅ Illinois (IL)
- ✅ Florida (FL)
- ✅ Georgia (GA)
- ✅ Pennsylvania (PA)
- ✅ Ohio (OH)
- ✅ Virginia (VA)
- ✅ And all other US states

#### Major US Cities
- ✅ San Francisco, CA
- ✅ New York City / NYC
- ✅ Seattle, WA
- ✅ Boston, MA
- ✅ Austin, TX
- ✅ Denver, CO
- ✅ Los Angeles, CA
- ✅ Chicago, IL
- ✅ Atlanta, GA
- ✅ Washington DC

---

## ❌ JOBS THAT WILL BE EXCLUDED

### High-Level/Senior Titles (NOT for 2-3 years exp)
- ❌ Staff Engineer
- ❌ Staff Data Scientist
- ❌ Staff Scientist
- ❌ Head of [Department]
- ❌ Director of [Department]
- ❌ Principal Engineer
- ❌ Principal Scientist
- ❌ VP Engineering
- ❌ Vice President
- ❌ CTO
- ❌ CFO
- ❌ CEO
- ❌ COO
- ❌ Distinguished Engineer
- ❌ Senior Director
- ❌ Group Manager
- ❌ Technical Lead (Senior)
- ❌ Lead Architect

### Not Relevant to Your Experience
- ❌ Student Programs
- ❌ University Recruiting
- ❌ Campus Ambassador
- ❌ Apprenticeship
- ❌ Volunteer Positions
- ❌ Unpaid Roles

### Locations (Non-US)
- ❌ London, UK
- ❌ Toronto, Canada
- ❌ Berlin, Germany
- ❌ Singapore
- ❌ India
- ❌ Any non-USA location

---

## Examples: What Gets Filtered

### ✅ WILL MATCH

```
Title: "Data Scientist"
Location: "San Francisco, CA, USA"
Result: ✅ ALERT SENT
Reason: Matches role + US location

---

Title: "Associate Machine Learning Engineer"
Location: "Remote (US)"
Result: ✅ ALERT SENT
Reason: Associate title + remote US

---

Title: "Junior Data Engineer"
Location: "New York, NY"
Result: ✅ ALERT SENT
Reason: Junior title + NYC

---

Title: "Data Scientist Intern"
Location: "Boston, MA"
Result: ✅ ALERT SENT
Reason: Intern + Massachusetts
```

### ❌ WON'T MATCH

```
Title: "Senior Data Scientist"
Location: "San Francisco, CA"
Result: ❌ EXCLUDED
Reason: "Senior" not allowed (above your level)

---

Title: "Staff ML Engineer"
Location: "Seattle, WA"
Result: ❌ EXCLUDED
Reason: "Staff" excluded (too senior)

---

Title: "Data Scientist"
Location: "London, UK"
Result: ❌ EXCLUDED
Reason: Non-USA location

---

Title: "Principal AI Engineer"
Location: "Remote"
Result: ❌ EXCLUDED
Reason: "Principal" excluded (too senior)

---

Title: "ML Researcher"
Location: "Toronto, Canada"
Result: ❌ EXCLUDED
Reason: Canada, not USA

---

Title: "Head of Data Science"
Location: "San Francisco, CA"
Result: ❌ EXCLUDED
Reason: "Head of" excluded (too senior)
```

---

## Configuration Files Updated

### 1. `/config/config.yaml`
**Section: `excluded_keywords`**

Added exclusions for:
- Staff, Head, Director, Principal, VP, Executive
- Senior Director, Distinguished, Fellow
- Lead Engineer, Technical Lead, Group Manager
- Kept: Co-op, Student, Campus, University (not relevant)
- **Removed:** "intern", "internship", "entry level" exclusions (you want these!)

### 2. `/config/keywords.yaml`
**Updated all role sections** to include:
- Associate [Role]
- Sr Associate [Role]
- Junior [Role]
- [Role] Intern
- Entry Level [Role]

---

## How Filtering Works

### Step 1: Job Title Check
```
Job Title: "Senior Data Scientist"
         ↓
Contains "Staff"? No
Contains "Head"? No
Contains "Director"? No
Contains "Senior"? ✅ YES → EXCLUDED
```

### Step 2: Location Check
```
Location: "London, UK"
         ↓
Contains "United States"? No
Contains "USA"? No
Contains valid US state? No
Contains valid US city? No
Result: ❌ EXCLUDED
```

### Step 3: Role Match
```
Job keywords: ["data scientist", "analytics", "SQL"]
Your roles: ["data_analyst", "data_scientist", ...]
         ↓
Matches "data_scientist"? ✅ YES
Contains excluded keywords? ❌ NO
Result: ✅ ALERT SENT
```

---

## Testing Your Filters

### Run a Check Now
```bash
python -m job_radar.cli check
```

### View Matching Jobs
```bash
# Check database for recent jobs
sqlite3 data/job_radar.db "SELECT title, location, alerted FROM jobs ORDER BY scraped_at DESC LIMIT 20;"
```

### View Logs
```bash
tail -50 data/alerts.log
```

---

## If You Need to Adjust

### Add more excluded keywords
Edit `/config/config.yaml` → `excluded_keywords` section

### Add more roles
Edit `/config/keywords.yaml` → add new role category or keywords

### Add more cities
Edit `/config/config.yaml` → `locations` section

### Change experience level cutoff
Edit `/config/config.yaml` → update role keywords with new seniority levels

---

## Summary

✅ **Strict Filtering Active**
- Only roles for 2-3 years of experience
- Only USA locations
- No high-level (Staff, Director, Principal, etc.) roles
- Includes internships, entry-level, associate, sr associate

**Current Status:** Ready to receive alerts
**Check Frequency:** Every 2 hours (10 PM - 6 AM PST: quiet hours)
