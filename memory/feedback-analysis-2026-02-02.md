# Feedback Loop Analysis — 2026-02-02

## What Worked

### High Engagement Categories
1. **Meta/system discussions** — Fast replies when discussing daemon improvement
2. **Capability demos** — Market Pulse TTS, NVDA dashboard got positive reactions
3. **Deep dives + investment angle** — US-China AI race got 👍
4. **Quick decisions** — Short action items get fast engagement

### Effective Patterns
- Lead with insight, not background
- Include investment angle when relevant
- Interactive conversation > broadcast outputs
- "Just do it" approach > asking permission

## What Didn't Work

### Low/Neutral Engagement
- **weekend-family-ideas** — Got 🤔 (uncertain). Too generic, needs personalization.
- **Stacked cron outputs** — Multiple surfaces without replies = message fatigue
- **Daily Status Email** — Overlaps with World State, disabled

### Failed Jobs (model error)
8 jobs failing due to `anthropic/claude-sonnet-4` vs `anthropic/claude-sonnet-4-0`
- **Fixed**: Updated all to use `sonnet` alias

## Actions Taken

### Model Fixes (8 jobs)
- daily-research-scan → `sonnet`
- Daily Status Email → `haiku` (then disabled)
- Daily SG News Briefing → `sonnet`
- NVDA Dashboard Refresh → `haiku`
- SpaceX IPO Tracker → `sonnet`
- Weekly Engagement Analysis → `haiku` (then disabled)
- Monday Research Digest → `sonnet`
- weekly-self-review → `sonnet`

### Consolidation (31 → 21 enabled)
Disabled:
- Daily Topic Self-Audit (overlaps weekly-self-review)
- Signal Watcher (broken, Brave API issue)
- weekly-checkin (low value, merge into Ambitious Proposal)
- AI Capex Narrative Monitor (covered in Monday Digest)
- Weekly Twitter/X Intel (expensive, sparse signal)
- Daily Status Email (overlaps World State)
- Embodied AI Tracker (covered in Research Paper)
- Weekly Forecast Calibration (merge into weekly-self-review)
- Weekly Engagement Analysis (merge into weekly-self-review)
- Monthly System Hygiene (keep Weekly Self-Maintenance)

### Kept (21 active crons)
**Daily:**
- Daily SG News Briefing (8am SGT)
- daily-research-scan (0:15 SGT)
- Daily World State Analysis (7:20 SGT)
- Daily Email Triage (8:45 SGT)
- NVDA Dashboard Refresh (8:15 SGT)

**Weekly:**
- weekly-synthesis (Sun 2am UTC)
- weekend-family-ideas (Sat/Sun 8:30 SGT)
- weekly-self-review (Mon 3:30 SGT)
- Weekly Ambitious Proposal (Sun 10pm SGT)
- Monday Research Digest (Mon 9am SGT)
- Research Paper Scan (Fri 10am SGT)
- Macro Pulse (Tue 9am SGT)
- Weekly Disk Cleanup (Sun 4am SGT)
- Weekly Self-Maintenance (Sun 2pm SGT)

**Periodic:**
- SpaceX IPO Tracker (Thu 9am SGT)
- Kids Dinner Ideas (Sun/Mon/Tue 8pm SGT)
- openclaw-update-check (Sun 10am SGT)
- 6-Hour Self-Assessment (every 6 hours)
- Watchlist Price Alerts (Mon-Fri 10pm/2am SGT)

**One-shot:**
- NVDA Earnings Reminder (Feb 24)
- Monthly Memory Compaction (1st of month)

## Patterns to Reinforce

1. **Model aliases > full paths** — Use `sonnet`, `haiku`, `opus` not full paths
2. **Interactive > broadcast** — Pause cron surfaces during active conversations
3. **Investment angle** — Always include for market-related surfaces
4. **Quality gate** — Max 3 proactive surfaces per day

## Next Optimization

- Fix Signal Watcher (Brave API), re-enable when working
- Add forecast calibration to weekly-self-review prompt
- Track engagement by job to identify more cuts
- Target: 18-20 crons (currently 21)
