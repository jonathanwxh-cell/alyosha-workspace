# Scheduling Research: Optimal Timing for Autonomous Tasks

*Date: 2026-02-02*
*Task: Research and implement scheduling improvements*

---

## Research Findings

### 1. General Notification Timing Research

| Finding | Source | Application |
|---------|--------|-------------|
| Peak engagement: 10am-1pm, peak at 11am | Leanplum | Surface insights mid-morning |
| Retail best: 8-9am and 6-8pm | MobiLoud | Bookend active day |
| Context-aware beats fixed schedule | ContextSDK | Match task type to time |
| Earlier in week > later | MobiLoud | Front-load important surfaces |

### 2. Jon-Specific Patterns (from feedback-log.jsonl)

| Pattern | Data | Implication |
|---------|------|-------------|
| Fast replies at 6am SGT | Observed | Early morning = high attention |
| Active 8am-11pm | Config | Wide window, need prioritization |
| High engagement: meta, research, deep-dive | Feedback log | Lead with substance |
| Variable mid-day | Observed | Kids, work interruptions |

### 3. Circadian Task Matching

Research on cognitive performance suggests:
- **Morning (6-10am):** Peak alertness, good for analytical tasks
- **Late morning (10am-12pm):** Peak working memory, good for complex content
- **Early afternoon (1-3pm):** Post-lunch dip, lighter content
- **Late afternoon (3-6pm):** Second peak, good for creative tasks
- **Evening (6-10pm):** Good for synthesis, reflection

---

## Current System Gaps

### Gap 1: Task Type Not Matched to Time
Current system adjusts *frequency* but not *content type*.

**Fix:** Add task-type weighting based on time of day.

### Gap 2: Backoff Rules Not Implemented
`scheduling-intelligence.json` has backoff rules that aren't used:
- `noReplyThreshold: 3`
- `backoffMultiplier: 1.5`
- `maxBackoffHours: 8`

**Fix:** Implement actual backoff tracking.

### Gap 3: No Burst Mode Detection
When Jon is actively engaged (multiple replies in short window), should accelerate.

**Fix:** Add burst mode multiplier.

### Gap 4: No Task Queue Intelligence
All tasks treated equally regardless of time appropriateness.

**Fix:** Add time-appropriate task filtering.

---

## Implementation Plan

### Phase 1: Backoff Tracking (Implementing Now)
- Track consecutive unreplied surfaces
- Apply backoff multiplier when threshold hit
- Reset on engagement

### Phase 2: Burst Mode (Implementing Now)
- Detect rapid engagement (2+ replies in 30min)
- Accelerate intervals during burst
- Decay back to normal

### Phase 3: Task-Time Matching (Future)
- Tag prompts with optimal time windows
- Filter/prioritize based on current time

---

## Code Changes

See: `scripts/adaptive-scheduler.py` (updated)
