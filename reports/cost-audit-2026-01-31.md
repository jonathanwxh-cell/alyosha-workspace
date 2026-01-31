# Cost Audit Report

*January 31, 2026*

---

## Summary

| Service | Status | Risk Level |
|---------|--------|------------|
| **Claude Opus** | Primary model | 💰 HIGH (most expensive) |
| **Apify** | Used for Reddit scraping | 💰 HIGH (Jon flagged as expensive) |
| **Brave Search** | Rate limited (Free tier) | ✅ LOW |
| **OpenAI** | Image gen only | ⚠️ MEDIUM |
| **Disk Storage** | 311MB workspace | ✅ LOW |

---

## Detailed Analysis

### 1. Model Costs (Highest Impact)

**Current:** `claude-opus-4-5` (most expensive Anthropic model)

| Model | Input | Output | Cache Read | Cache Write |
|-------|-------|--------|------------|-------------|
| Opus 4.5 | $15/M | $75/M | $1.875/M | $18.75/M |
| Sonnet 4 | $3/M | $15/M | $0.30/M | $3.75/M |

**Estimate for today's session:**
- Heavy usage (3 deep dives, multiple tools, long conversations)
- Rough estimate: ~500K input tokens, ~100K output tokens
- Cost: ~$15-25 for today alone

**Recommendation:** 
- Use Opus for complex tasks (research, coding, creative)
- Switch to Sonnet for routine tasks (status checks, simple queries)
- Can set per-session model override: `/model sonnet`

### 2. Apify (Flagged by Jon as Expensive)

**Current usage:**
- `Daily SG News Briefing` cron mentions Apify
- `scripts/reddit-sg.sh` uses Apify Reddit scraper

**Apify pricing:**
- Pay per compute unit (~$0.25-0.50 per actor run)
- Reddit scraper: ~$0.10-0.30 per run
- If Daily SG News runs daily: ~$3-9/month just for Reddit

**Recommendation:**
- ✅ Already noted in TOOLS.md: "Use as last resort only"
- Remove Apify from Daily SG News cron (use web_search instead)
- Keep `reddit-sg.sh` but use sparingly (manual only)

### 3. Cron Jobs (10 Active)

| Job | Frequency | Model Cost Est. |
|-----|-----------|-----------------|
| Daily SG News | Daily 8am | ~$1-2/run |
| Daily Research Scan | Daily 8:15-10:15am | ~$0.50-1/run |
| Weekend Family Ideas | Sat/Sun 8:30am | ~$0.50/run |
| World Models Tracker | Mon 9am | ~$0.30/run |
| AI Capex Monitor | Mon/Wed/Fri 8am | ~$0.30/run |
| Weekly Synthesis | Sun 10am | ~$0.50/run |
| Weekly Self-Review | Mon 11am | ~$0.50/run |
| Weekly Check-in | Wed 8pm | ~$0.30/run |
| Monthly Memory Compaction | 1st of month | ~$0.50/run |
| Self-Report | One-shot (tomorrow) | ~$1/run |

**Monthly estimate:** ~$50-100 just from cron jobs

**Recommendations:**
- Consolidate similar jobs (e.g., combine research + capex monitor)
- Add "stay silent if nothing found" to all jobs (some already have this)
- Consider running some weekly instead of daily

### 4. Brave Search (Free Tier)

**Current:** Free plan (2,000 queries/month, 1 req/sec rate limit)

**Usage:** Hit rate limit several times today during research

**Recommendation:**
- Sufficient for current usage
- If daemon scales up, may need paid tier (~$5/month for 5K queries)

### 5. Disk Storage

| Location | Size | Notes |
|----------|------|-------|
| Workspace | 311MB | Reports, scripts, memory |
| Session transcripts | 25MB | Growing over time |
| Logs | 68KB | Reasonable |

**Recommendation:** 
- ✅ Memory compaction already scheduled (monthly)
- Transcript cleanup may be needed eventually (not urgent)

---

## Inefficiencies Found

### 1. Daily SG News + Apify
**Issue:** Uses Apify for Reddit when web_search could work
**Fix:** Update cron payload to use Brave Search instead

### 2. Opus for Everything
**Issue:** Using most expensive model even for simple tasks
**Fix:** Add model selection logic based on task complexity

### 3. Overlapping Cron Jobs
**Issue:** Multiple jobs run at similar times (8-10am SGT)
**Fix:** Spread out or consolidate

### 4. No Cost Tracking
**Issue:** No visibility into actual API spend
**Fix:** Could add a cost estimation to daily logs

---

## Recommended Actions

### Immediate (High Impact)

1. **Fix Daily SG News cron** — Remove Apify, use web_search
```
Change: "Use Apify to scrape r/singapore"
To: "Search for Singapore news and Reddit highlights using web_search"
```

2. **Add model switching** — Use Sonnet for routine tasks

### Medium Term

3. **Consolidate cron jobs** — Merge overlapping monitors
4. **Add cost logging** — Track token usage per session

### Low Priority

5. **Session transcript cleanup** — Add to monthly compaction
6. **Consider Brave paid tier** — If search needs increase

---

## Monthly Cost Estimate

| Item | Low | High |
|------|-----|------|
| Main session (Opus) | $100 | $300 |
| Cron jobs | $50 | $100 |
| Apify (if kept) | $5 | $15 |
| **Total** | **$155** | **$415** |

**With optimizations (Sonnet for routine, no Apify):**
| Item | Low | High |
|------|-----|------|
| Main session (mixed) | $50 | $150 |
| Cron jobs (Sonnet) | $20 | $50 |
| **Total** | **$70** | **$200** |

---

*Savings potential: 50-60% with model switching + Apify removal*
