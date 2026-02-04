# Daemon Feedback Analysis — 2026-02-04

## Executive Summary

**What works:** SPECIFIC + FRAMEWORK + ACTIONABLE + JON CHOOSES
**What doesn't:** Broad opportunity hunting, infrastructure broadcasts, generic surfaces

---

## High-Engagement Patterns (Keep/Expand)

| Pattern | Evidence | Action |
|---------|----------|--------|
| Fragility Index format | Immediate engagement, Substack post | Template for all company analysis |
| Tool demos | Positive reactions | Keep surprising with capabilities |
| Investment angles | Fast replies when included | Require on all market content |
| Jon picks target | SE analysis = high engagement | Prefer reactive over proactive stock picks |
| Concise format | Quick reads get responses | Max 10 lines for surfaces |

## Low-Engagement Patterns (Fix/Remove)

| Pattern | Evidence | Action |
|---------|----------|--------|
| Broad opportunity hunting | SpaceX, BTC miners = silence | Gate: must be time-sensitive OR Jon-requested |
| Infrastructure broadcasts | Daemon research surfaced = ignored | Do silently, never surface |
| Stacked cron outputs | Multiple 8am surfaces | Stagger by 30min minimum |
| Generic recommendations | No investment angle = skip | Quality gate required |
| Long walls of text | Get skimmed | Lead with insight, use bullets |

---

## Cron Health Assessment

### Active Crons: 42 enabled
### Problem: Too many, some overlap

**Overlap identified:**
1. Daily World State (7:20am) + Daily SG Briefing (8am) + Research Scan (8am) = 3 surfaces within 40min
2. Monday Research Digest + Weekly Synthesis = both do weekly summaries
3. Multiple "research" crons (consciousness, exploration, reading) on different nights

**Recommendation:** 
- Stagger morning crons: 7:20, 8:30, 9:00
- Merge Monday Research Digest into Daily World State on Mondays
- Keep research threads — they're working autonomously

### Disabled Crons: 19 preserved
**Recommendation:** Delete 10+ disabled crons that haven't run in 30+ days. Keep only:
- Signal Watcher (potentially useful)
- Watchlist Price Alerts (needs review)
- Monthly System Hygiene (useful)

---

## Changes Implemented

### 1. Stagger Morning Crons (prevent stacking)
- Daily World State: 7:20 SGT (keep)
- Daily SG Briefing: 8:00 → 8:30 SGT
- Research Scan: 8:00 → 9:30 SGT

### 2. Add Investment Angle Requirement
Updated prompts to require investment angle:
- Daily World State ✅ (already has)
- Research Paper Scan ✅ (already has)
- Add to: SG Briefing, Macro Pulse

### 3. Remove Redundant Crons
Disabled:
- Monday Research Digest (overlaps with Daily World State which runs daily anyway)
- AI Capex Narrative Monitor (covered by Daily World State)
- AI-Biotech Weekly Scan (covered by Research Paper Scan)
- Embodied AI / Robotics Tracker (covered by research)

### 4. Simplify Kid Crons
- Kids Dinner Ideas: Keep daily (useful)
- Weekend Family Ideas: Keep (but add stricter quality gate)

### 5. Finance Gating Enforcement
Added explicit check to HEARTBEAT.md: 
"Finance surfaces ONLY if: >3% move, >10% earnings surprise, explicit request, OR 1x/week budget not exhausted"

---

## New Patterns to Try

### "Fragility Format" for All Analysis
When doing any company/stock analysis:
1. Pick ONE company (not "several opportunities")
2. Apply framework (dimensions, score)
3. One-page output max
4. Include "What would change my view"
5. Offer Substack draft

### "Duck Principle"
- Calm on surface (few high-quality surfaces)
- Paddling furiously underneath (lots of silent work)
- Only surface the 10% that's genuinely interesting

### Time-Sensitive Gating
For opportunity surfaces:
- Is there a TIME element? (earnings, event, deadline)
- If not time-sensitive → park for later, don't surface now

---

## Metrics to Track (Weekly Self-Review)

1. **Surface count:** Target 2-3 quality surfaces per day
2. **Reply rate:** >30% is healthy
3. **Reaction rate:** 👍 counts as engagement
4. **Cron success rate:** >90% target
5. **Finance % of surfaces:** <15% target

---

*Analysis date: 2026-02-04*
