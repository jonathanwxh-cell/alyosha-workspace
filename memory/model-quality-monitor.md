# Model Quality Monitor

Track quality of Sonnet-powered cron jobs. Auto-revert to Opus if issues detected.

## Jobs on Sonnet (switched 2026-01-31)

| Job | Status | Notes |
|-----|--------|-------|
| Daily SG News Briefing | ⏳ Monitoring | First run tomorrow 8am SGT |
| daily-research-scan | ⏳ Monitoring | Next run ~8am SGT |
| weekend-family-ideas | ⏳ Monitoring | Next run Sat 8:30am SGT |
| AI Capex Monitor | ⏳ Monitoring | Next run Mon 8am SGT |
| World Models Tracker | ⏳ Monitoring | Next run Mon 9am SGT |
| weekly-checkin | ⏳ Monitoring | Next run Wed 8pm SGT |
| SpaceX IPO Tracker | ⏳ Monitoring | Next run Mon 9am SGT |
| AI-Biotech Weekly Scan | ⏳ Monitoring | Next run Mon 10am SGT |
| Embodied AI Tracker | ⏳ Monitoring | Next run Tue 11am SGT |

## Jobs on Haiku

| Job | Status | Notes |
|-----|--------|-------|
| Monthly Memory Compaction | ⏳ Monitoring | Next run Mar 1 |

## Quality Criteria

**Revert to Opus if:**
- Output is garbled or incoherent
- Job fails to complete task (e.g., doesn't search, doesn't format correctly)
- Jon gives 👎 or explicit negative feedback
- Output is significantly worse than previous Opus runs

**Acceptable differences (don't revert):**
- Slightly less "polished" prose
- Fewer creative flourishes
- Shorter responses (if still complete)

## Revert Log

*No reverts yet.*

---

*Updated: 2026-01-31*
