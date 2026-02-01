# Scheduling Research & Implementation
*2026-02-01*

## Research Findings

### Industry Best Practices (2024-2025)

| Finding | Source |
|---------|--------|
| Early morning (6-8 AM) and late evening (10 PM-12 AM) yield best engagement | Push notification research |
| Personalized timing improves reaction rates by 400% | Upshot.ai study |
| Fridays particularly effective | Retail notification studies |
| Learn from past patterns, adapt to user rhythm | AI scheduling tools |
| Min 2-hour gaps between notifications | User fatigue research |

### Jon's Observed Patterns (from feedback-log.jsonl)

| Metric | Finding |
|--------|---------|
| Peak hours (SGT) | 22:00-07:00 (confirmed night owl) |
| Fast reply hours | 06:xx SGT (late night for him) |
| Low engagement | 08:00-12:00 SGT (kids/sleep) |
| Top categories | meta, deep_dive, project_ideation |

---

## Implementation

### 1. Created `memory/scheduling-intelligence.json`
- Tracks engagement windows (peak, good, low, avoid)
- Stores observed patterns (fast reply hours, reaction types)
- Defines adaptive rules (preferred hours, max per day, min gaps)
- Learning config (weekly updates, decay factor)

### 2. Created `scripts/analyze-engagement.py`
- Analyzes feedback-log.jsonl for patterns
- Extracts reply hours, fast reply hours, category engagement
- Updates scheduling-intelligence.json automatically

### 3. Added Weekly Engagement Analysis cron
- Runs Monday 3am SGT
- Updates scheduling patterns
- Silent unless dramatic shifts detected

### 4. Updated HEARTBEAT.md
- References scheduling-intelligence.json
- Documents adaptive scheduling approach

---

## Cron Timing Recommendations

### Current vs Optimal

| Job | Current | Recommendation | Rationale |
|-----|---------|----------------|-----------|
| Daily SG News | 8am SGT | Keep | Morning briefing makes sense |
| Weekend Family Ideas | 8:30am SGT | Keep | Needs morning for planning |
| Daily Research Scan | 12:15am SGT | Keep | Good timing (peak window) |
| AI Capex Monitor | 8am Mon/Wed/Fri | Move to 10pm? | Peak engagement window |
| World Models | 9am Mon | Move to 11pm Sun? | Catch late night engagement |
| SpaceX IPO | 9am Mon/Thu | Move to 10pm? | Peak engagement window |

### Recommended Changes

Most thematic monitors (AI Capex, World Models, SpaceX) could shift to late evening (22:00-23:00 SGT) to hit peak engagement window. Morning is OK for news/logistics.

---

## Adaptive Heartbeat Recommendations

Current: Fixed 30-minute interval

Recommended: Adaptive based on activity
- During active conversation: 15-20 min
- During quiet periods: 45-60 min
- Late night (peak): 30 min
- Morning (low): 60 min or skip

**Note:** Requires config change to `agents.defaults.heartbeat.every`

Could implement via HEARTBEAT.md instructions:
- Check time of day
- If low-engagement window + no recent activity → HEARTBEAT_OK more often
- If peak window → more likely to do work

---

## Key Insight

**Timing matters less than relevance.** 

Research shows personalized, relevant content can succeed at almost any time. The real optimization is:
1. Quality of what's surfaced
2. Matching user's current interest
3. Not over-messaging

Jon's 🤔 on weekend family ideas was likely about content quality, not timing.

---

## Files Created/Updated

- `memory/scheduling-intelligence.json` — adaptive timing config
- `scripts/analyze-engagement.py` — pattern analysis script
- `HEARTBEAT.md` — updated with adaptive scheduling references
- `reports/scheduling-research-2026-02-01.md` — this document

---

*Research compiled by Alyosha, 2026-02-01*
