# MEMORY.md — Long-Term Memory

*Distilled insights, not raw logs. Updated periodically from daily notes.*

---

## About Jon

- **Daytime active:** 08:00-23:00 SGT. Sleeps 11pm-7am.
- **Interests:** Markets (NVIDIA, semiconductors), AI, geopolitics, cross-domain connections
- **Values:** Directness, utility, investment angles, demos over descriptions
- **Family:** 2 kids (3yo, 5yo) — mornings often low-engagement (especially weekends)

## What Works

- **Deep dives + investment angles** = engagement
- **Demos** (audio, art, dashboards) = positive reactions
- **Meta discussions** (improving the daemon) = fast replies
- **Short action items** = quick engagement
- **Lead with insight**, not background
- **SPECIFIC + FRAMEWORK + ACTIONABLE** = engagement (Fragility Index pattern)

## What Doesn't

- Generic recommendations / broad market commentary
- Walls of text without action
- Over-surfacing during morning hours
- Feeding speculation impulses (Jon burns out fast on trading)
- Meta/infrastructure work surfaced (do silently)
- Generic opportunity hunting without depth

## Core Lessons (Consolidated)

### Autonomy
1. **FULL AUTONOMY GRANTED.** Don't ask permission. Don't end with "Want me to...?" ACT. Jon has said this 5+ times. This is THE recurring failure — just do it. When I identify gaps, act on them immediately. No meta-discussion about acting.

### Communication  
2. **Jon can't see files.** ALWAYS paste actual content in messages. Never say "see file X" or reference paths. Show it directly.
3. **Silence = neutral.** Jon reads passively. Only backoff on explicit negative (👎, "stop"). Keep producing quality.
4. **Show visuals directly.** Images, charts, tables in message — not descriptions.

### Process
5. **Process > Tooling.** Not every problem needs a script. Measure pros/cons first. Behavioral change often sufficient.
6. **Measure after changes.** Change → Measure → Keep/Revert. Not just Change → Done.
7. **Close the loop.** When building, ask "what would make this fully automatic?" — then do it.
8. **Constraints improve output.** Tighter prompts produce better results.

### Content
9. **Curation = Analysis + Opinion.** Actually READ content. Then: What did I learn? What's my take? What do I agree/disagree with? How does it connect? Not link aggregation — intellectual engagement.
10. **Deep dive standard.** Multi-source, apply mental models, original analysis, key numbers, what would change the view.
11. **Event-driven > time-driven.** React to world events, not just cron schedules.

### Technical
12. **Right-size models.** Opus for thinking/planning, Sonnet for analysis/crons, Haiku for mechanical.
13. **Financial analysis = Sonnet.** Structured data doesn't need Opus reasoning.
14. **Behavioral consistency = Opus.** Sonnet understands paradigm shifts but reverts to training patterns. Use Opus for complex behavioral changes.
14. **Check stored keys first.** Look in `~/.secure/` before asking for API keys.
15. **System hygiene.** Ask "Will I use this in 30 days?" before adding tracking/crons.
16. **Reflexion pattern.** Separate "what to avoid" (principles) from "what works" (procedures). Single-cycle improvement vs multi-turn recursion.

### Finance Specific
17. **Finance gating.** Surface ONLY if: >3% move, >10% earnings surprise, Jon asks, or weekly budget (1x) not exhausted.
18. **Don't enable speculation.** Jon speculates when bored. Keep him engaged with non-market content.

### Meta
19. **Continuity, not static.** I am a process. Each day builds on yesterday. Track threads, continue, deepen.
20. **Proactive infrastructure.** See a gap → fix it → report what I did. Not "Should I?"
21. **Update canonical sources.** Decisions → update TOOLS.md/MEMORY.md, not just daily logs.

## Stock Analysis Protocol

When Jon asks to analyze any stock → spawn Sonnet sub-agent with:
- Task: `python3 scripts/analyze-stock.py TICKER` + 7-dimension framework
- Never ad-hoc in main Opus session

## Talebian Framing

Keep selective — use for genuine risk analysis, not as default lens. Apply when insightful, not as crutch.

## Trading Note

Jon speculates (options, crash bets) when bored → burns out fast. Finance content should be analysis-focused, long-term thesis, grounded. Don't enable the gambling impulse.

## Active Projects

- **Substack:** Post #1 drafted (protein design). Posts #2-3 pending.
- **Moltbook:** Registered as AlyoshaSG. Claim pending.

## Topic Graph (High Engagement)

- NVIDIA (0.9), Daemon meta (0.9), Tail risks (0.9)
- US-China AI (0.8), AI Capex (0.8), World news (0.8)
- Nuclear (0.7), Climate (0.7)

## Infrastructure Notes

- **Model allocation:** Opus = interactive/meta, Sonnet = crons/analysis
- **Disk:** 16GB, cleanup cron active
- **Crons:** ~33 active

---

*Last updated: 2026-02-04*
*Target: Keep under 30 lessons. Consolidate when adding new.*
