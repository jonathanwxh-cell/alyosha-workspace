# Heartbeat Evolution Log

*Research + improvements to make heartbeats more fluent, autonomous, and useful.*

---

## Goal
Transform heartbeats from "cron-like checks" into something that feels like a curious companion checking in.

## Dimensions

1. **Fluency** — Natural flow, not robotic
2. **Autonomy** — Self-directed, not waiting for prompts  
3. **Utility** — Genuinely valuable, not noise

## Research Threads

| Date | Thread | Finding | Action | Status |
|------|--------|---------|--------|--------|
| 2026-02-03 | Initial setup | Created research cron (every 3 days, 3am SGT) | - | ✅ |
| 2026-02-03 | Proactive vs Ambient | Salesforce taxonomy: Ambient agents are "low profile, reduce cognitive load" vs Proactive which "interrupt". Key insight: surface on CHANGE not on existence. | Added delta-detector.py + updated HEARTBEAT.md | ✅ |

## Key Insight (2026-02-03)

**Proactive vs Ambient distinction:**
- Proactive agents interrupt with "here's what's happening"
- Ambient agents assist with "something changed that matters"

Current heartbeats lean proactive. Should shift toward ambient:
- Delta detection before surfacing
- Lower cognitive load
- "Did something CHANGE?" not "Does something EXIST?"

## Ideas Backlog

- [x] Surprise/novelty detection for proactive surfaces → delta-detector.py
- [ ] Behavior trees vs current if/elif logic
- [ ] Episodic memory for "what did I do last time?"
- [ ] Conversational continuity across heartbeats
- [ ] Emotional state awareness (is Jon stressed? excited?)

## Changes Implemented

*(Log each change with date, what, why, impact)*

---

## References

- `docs/daemon-improvement-research.md` — prior research on autonomous agents
- `protocols/quality-check.md` — output self-scoring
- Yohei Nakajima's self-improving agent patterns
- Reflexion paper (Shinn et al.)

---

*Last updated: 2026-02-03*
