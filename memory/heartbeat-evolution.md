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
| 2026-02-03 | Behavior Trees | Current heartbeat logic uses if/elif chains → hard to maintain as complexity grows. BTs offer: (1) Modularity - standardized interface (success/failure/running), (2) Reactivity - priority interrupts naturally, (3) Visual debugging. Key: "ticking" pattern + hierarchical control flow. | scripts/heartbeat-bt.py - working prototype with modular nodes | ✅ |
| 2026-02-03 | Episodic Memory | Current heartbeat-state.json is basic key-value. Missing: (1) "What did I do last time in this context?", (2) Pattern recognition across sessions, (3) Learning from past failures. Key insight: Episodic (short-term task memory) vs Semantic (long-term knowledge). Need episodic for continuity. | scripts/episodic-memory.py - context-aware action tracking | ✅ |

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
- [x] Behavior trees vs current if/elif logic → scripts/heartbeat-bt.py
- [x] Episodic memory for "what did I do last time?" → scripts/episodic-memory.py
- [ ] **Integration:** Replace HEARTBEAT.md logic with BT system
- [ ] **Learning:** Connect episodic memory to actual heartbeat outcomes
- [ ] Conversational continuity across heartbeats
- [ ] Emotional state awareness (is Jon stressed? excited?)
- [ ] **Decorator nodes:** Time-gating, cooldowns, probability-based actions
- [ ] **Parallel nodes:** Background tasks while main heartbeat runs
- [ ] **Blackboard pattern:** Shared memory between BT nodes

## Changes Implemented

*(Log each change with date, what, why, impact)*

### 2026-02-03: Behavior Tree Architecture Prototype

**What:** Created `scripts/heartbeat-bt.py` - a modular behavior tree system for heartbeat decision logic.

**Key features:**
- Modular nodes: SequenceNode (all must succeed), FallbackNode (try until one succeeds), ConditionNode, ActionNode
- Priority-based execution: Urgent alerts → Active conversation detection → Delta detection → Creative work → Default
- Standardized interface: All nodes return SUCCESS/FAILURE/RUNNING
- Easily extensible: Add new branches without touching existing logic

**Why:** Current if/elif chains become unmaintainable as complexity grows. BTs provide visual debuggability and modular composition.

**Impact:** Foundation for more sophisticated autonomous behavior. Tested successfully with delta-detector integration.

### 2026-02-03: Episodic Memory System

**What:** Created `scripts/episodic-memory.py` - context-aware action tracking and pattern recognition.

**Key features:**
- Records actions with context (time slot, day type, recent activity)
- Pattern suggestions: "What do I normally do in this context?"
- Engagement tracking: Learn from Jon's responses to improve decisions
- Break pattern detection: When to try something different
- Context hashing: Group similar situations for pattern matching

**Why:** Current heartbeat-state.json lacks memory of past actions and their outcomes. Need "what did I do last time?" continuity.

**Impact:** Enables learning from experience and more natural behavioral evolution over time.

---

## References

- `docs/daemon-improvement-research.md` — prior research on autonomous agents
- `protocols/quality-check.md` — output self-scoring
- Yohei Nakajima's self-improving agent patterns
- Reflexion paper (Shinn et al.)

---

*Last updated: 2026-02-03*
