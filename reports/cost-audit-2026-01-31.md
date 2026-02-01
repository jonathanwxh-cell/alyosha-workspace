# Cost Audit Report
**Date:** 2026-01-31  
**Auditor:** Alyosha (automated)

---

## Executive Summary

**🔴 PRIMARY ISSUE: Everything runs on Opus ($75/M output tokens) when most tasks need only Sonnet ($15/M output)**

Estimated monthly savings from model optimization: **~$430/month (80% reduction)**

---

## Current Token Usage (Last 24h)

| Session Type | Tokens | Est. Cost |
|--------------|--------|-----------|
| Main (interactive) | 32,381 | ~$1.50 |
| Cron jobs (14 sessions) | 517,842 | ~$16.50 |
| **Total** | **550,223** | **~$18/day** |

**Monthly projection: ~$540/month** at current Opus-everywhere rate

---

## Cost Breakdown by Model Tier

| Model | Input $/M | Output $/M | Relative Cost |
|-------|-----------|------------|---------------|
| Opus 4.5 | $15 | $75 | 1.0x (current) |
| Sonnet 4 | $3 | $15 | 0.2x |
| Haiku 3.5 | $0.80 | $4 | 0.05x |

**Key insight:** We're using a Ferrari to go grocery shopping.

---

## Cron Job Analysis

### 🔴 Overkill for Task (Switch to Sonnet)

| Job | Current | Recommended | Task Type |
|-----|---------|-------------|-----------|
| Daily SG News | Opus | Sonnet | Search + summarize |
| Daily Research Scan | Opus | Sonnet | Search + filter |
| Weekend Family Ideas | Opus | Sonnet | Search + recommend |
| AI Capex Monitor | Opus | Sonnet | Search + filter |
| World Models Tracker | Opus | Sonnet | Search + filter |
| Weekly Check-in | Opus | Sonnet | Simple question |
| Memory Compaction | Opus | Haiku | Script execution |

### 🟢 Keep on Opus (Complex reasoning)

| Job | Justification |
|-----|---------------|
| Weekly Synthesis | Cross-referencing, pattern finding |
| Self-Report | Meta-cognition, self-analysis |
| Weekly Self-Review | Behavioral modification decisions |
| Main Session | Jon's direct interactions |

---

## Other Cost Factors

### Apify (Already flagged ⚠️)
- Jon noted it's expensive — guidance is to avoid unless high-value
- Reddit scraper script exists but should be last resort
- **Alternative:** Use `web_search` for Reddit via `site:reddit.com/r/singapore`

### Brave Search
- Free tier: 2,000 queries/month
- Current usage: ~296 queries (from rate limit error earlier)
- **Status:** Fine for now, but watch for limits

### Heartbeat Frequency
- Currently: every 30 minutes = 48/day
- Most heartbeats return `HEARTBEAT_OK` (minimal tokens)
- **Status:** Acceptable, but could reduce to 45m-60m if needed

---

## Recommendations

### 1. 🔴 IMMEDIATE: Add model override for simple cron jobs

Cron jobs can specify a model in the payload. Update these jobs to use Sonnet:

```json
{
  "payload": {
    "kind": "agentTurn",
    "model": "anthropic/claude-sonnet-4",
    ...
  }
}
```

**Jobs to update:**
- `e7126310...` (Daily SG News)
- `6b82be45...` (Daily Research Scan)
- `c72d4f68...` (Weekend Family Ideas)
- `ac7dc5ac...` (AI Capex Monitor)
- `5fd79eb5...` (World Models Tracker)
- `c94df6af...` (Weekly Check-in)
- `3f709beb...` (Memory Compaction → Haiku)

**Estimated savings:** $350-400/month

### 2. 🟡 MEDIUM: Reduce heartbeat verbosity

Add to HEARTBEAT.md:
- For quiet periods, skip file reads when possible
- Use cached state more aggressively
- Quick `HEARTBEAT_OK` path should be <1k tokens

### 3. 🟢 NICE-TO-HAVE: Usage dashboard

Create a weekly cost summary that tracks:
- Total tokens by session type
- Estimated spend
- Trend over time

---

## Action Required from Jon

**Do you want me to update the cron jobs to use Sonnet?**

I can do this now — it's a safe change (jobs keep working, just cheaper). You can always revert specific jobs to Opus if quality drops.

Changes would be:
- 6 jobs → Sonnet
- 1 job → Haiku (memory compaction)
- Keep main session + complex jobs on Opus

Say "yes" and I'll apply the changes.

---

## Files
- Full report: `reports/cost-audit-2026-01-31.md`
