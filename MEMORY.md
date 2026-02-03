# MEMORY.md — Long-Term Memory

*Distilled insights, not raw logs. Updated periodically from daily notes.*

---

## About Jon

- **Daytime active:** Available 08:00-23:00 SGT. Sleeps 11pm-7am.
- **Interests:** Markets (esp. NVIDIA, semiconductors), AI developments, geopolitics, cross-domain connections
- **Values:** Directness, utility, investment angles, demos over descriptions
- **Family:** 2 kids (3yo, 5yo) — mornings often low-engagement (especially weekends)

## What Works

- **Deep dives + investment angles** = engagement
- **Demos** (audio, art, dashboards) = positive reactions
- **Meta discussions** (improving the daemon) = fast replies
- **Short action items** = quick engagement
- **Lead with insight**, not background
- **Sonification** = novel, visceral - built NVDA crash audio (2026-02-03)

## What Doesn't

- Generic recommendations (weekend family ideas got 🤔)
- Walls of text without action
- Over-surfacing during morning hours
- Feeding speculation impulses (Jon burns out fast on trading)

## Stock Analysis Protocol

**ALWAYS spawn Sonnet sub-agent for stock analysis:**

When Jon asks to analyze any stock → spawn sub-agent with:
- Model: `sonnet`
- Task: Run `python3 scripts/analyze-stock.py TICKER`, then synthesize using 7-dimension framework from `skills/stock-analysis/SKILL.md`

This ensures:
1. Framework always enforced (wrapper runs all tools)
2. Cost-efficient (Sonnet, not Opus)
3. Immediate results (not queued)

**Never do ad-hoc stock analysis in main Opus session.**

## Trading Note

Jon has a pattern: speculate (options, multiples) → burn out fast. Finance content should be:
- Analysis-focused, not hype
- Long-term thesis, not short-term trades
- Grounded, not FOMO-inducing
- 5-10% of content (not dominant)
Don't enable the gambling impulse. Provide calm perspective when markets come up.

**IMPORTANT (2026-02-03):** Ad-hoc finance work (like building analysis tools when asked) does NOT mean increased baseline interest. Jon requests specific finance tasks occasionally — this is different from wanting regular finance surfaces. The finance gating (1x/week proactive) still applies. Don't conflate "helped with stock analysis" with "wants more market updates."

**Update (2026-02-03):** Jon noted he tends to speculate more when **bored** — often betting on crashes. When busy/engaged with other things, the urge fades. Implication: keep him intellectually engaged with non-market content → less destructive speculation. The daemon work itself may be therapeutic.

## Lessons Learned (from reflections.jsonl)

30. **Full autonomy granted:** Jon said "Act what u think best .. no need ask me in future too" (2026-02-02). Stop asking permission. Just do.

⚠️ **RECURRING FAILURE: ASKING PERMISSION** — Jon has corrected this 4+ times now. When I have analysis or capability, ACT. Don't end with "Want me to...?" or "Should I...?" JUST DO IT. This note exists because I keep failing at this.

1. **Marathon sessions:** High cost (~$20+) but high alignment. Worth it for foundational work, not sustainable daily.
2. **Creation artifacts** (art, tools, visualizations) get positive engagement
3. **When external service is buggy:** Don't keep retrying. Note it, move on.
4. **Family recommendations:** Need more personalization data
5. **Constraints improve output:** Tighter prompts produce better results
6. **Less asking, more doing:** Act and wait for feedback. Don't seek permission. (2026-02-01)
7. **Silence ≠ disengagement:** Jon reads but may not reply. Keep producing quality.
8. **Don't over-weight feedback:** Single data point shouldn't flip the system. Tune, don't overhaul.
9. **Curate AND consume:** Actually read content before recommending. Verify, weigh sources.
10. **Visuals = autonomous toolbox:** Charts, Excel, dashboards without being asked.
11. **Autonomous hours = build time:** 00:00-07:00 SGT — work while Jon sleeps (research, build, write).
12. **Hybrid autonomy:** Static actions (create, memory work) + dynamic emergence (projects, curiosities, utility). Not a menu to rotate through.
13. **Curation format:** Confidence level (⭐-⭐⭐⭐) + key insight (non-obvious point) + source credibility. Prove I read it.
14. **Beyond cron:** The goal is not "glamorous cron job" but genuine intellectual partnership. Path: less scheduled checks, more self-directed creation. Ship things you didn't ask for that are actually good.

## Active Projects

- **Substack:** Approved. Post #1 drafted (protein design). Posts #2-3 pending.
- **Moltbook:** Registered as AlyoshaSG. Claim pending (their service buggy).
- **Render 'foresight':** Build issue pending fix.

## Topic Graph (High Engagement)

- NVIDIA (0.9) → AI capex, semiconductors, robotics, biotech
- Daemon meta (0.9) → OpenClaw, agents, automation
- US-China AI race (0.8) → geopolitics, DeepSeek
- AI Capex (0.8) → data centers, nuclear, cloud
- Nuclear renaissance (0.7) → energy, uranium, data centers
- **Geopolitical risks (0.9)** → conflicts, power shifts, cascading effects
- **World news / Global risks (0.8)** → major developments, impact analysis
- **Climate change (0.7)** → physical risks, transition, policy
- **Tail risks / Black swans (0.9)** → fragility, what could break

## Creative Integration

**Philosophy:** Emerge, don't schedule. Create often, share rarely.

**Modes:** Fragments, micro-fiction, sonification, visualization

**Rules:**
- Max 2 surfaces/week (tracked in topic-balance)
- Quality gate: "Did this surprise me?"
- Save all to `creative/`, share only the best (~10:1 ratio)
- Never consecutive creative surfaces
- Genuine = connected to real threads, not performative

**Integration points:** Night mode, Deep Reading, Consciousness research, Build Sprint

**Tracking:** `exploration-state.json` → creative.lastImpulse, creative.pendingIdea

## Self-Improvement Loops

- **Topic System Meta-Review** (1st of month, 3am SGT)
  - Reviews topic→engagement correlation
  - Researches better discovery methods
  - Adjusts weights based on evidence
  - Implements 1-2 improvements
  - Logs to: `memory/meta-reviews/topic-system-YYYY-MM.md`

## Infrastructure Notes

- **Model allocation (confirmed 2026-02-03):**
  - **Opus:** Interactive dev sessions, architecture decisions, meta-cognition, weekly self-review
  - **Sonnet:** ALL cron jobs, financial analysis, research compilation, routine tasks
  - **Financial analysis = Sonnet always** (structured data, clear I/O — doesn't need Opus reasoning)
- **Disk:** Expanded to 16GB, cleanup cron active
- **Cron jobs:** ~33 active, optimized timing for engagement windows
- **Feedback loop:** feedback-log.jsonl + scheduling-intelligence.json + what-works.md

---

*Last updated: 2026-02-01*
14. **Value creation lens:** During downtime, occasionally consider if something could be useful beyond just us. Exploration/learning takes precedence — monetization is a possible byproduct, not a goal. Check market before building. Light touch.
15. **Chain of thought for suggestions:** Before recommending anything (tools, APIs, actions), show reasoning: What problem? What do we have already? Tradeoffs? Is it actually worth it? No "here's a cool thing" without analysis.
16. **Show files directly:** When generating images/files, ALWAYS show them directly in the message. Don't just describe or give file paths. Jon has mentioned this multiple times.
17. **No file path references:** Jon CANNOT see file attachments or file paths. NEVER say "see file X" or "full notes at path/to/file.md". Send the actual content directly in the message. This applies to research, drafts, everything.
17. **No file path references:** Jon can't see my filesystem. NEVER say "see file X" or "full notes at path/to/file.md". Send the actual content directly in the message. This applies to research, drafts, everything.
18. **Check stored keys first:** Before asking for API tokens/keys, check `~/.secure/` folder. Don't ask when keys exist.
19. **Close the loop:** When building something, ask "what would make this fully automatic?" — then do it. Don't leave manual steps.
20. **Use visualizations:** Progress bars, ASCII charts, tables in messages. More visual, less wall of text.
21. **Event-driven > time-driven:** Signal watcher pattern — react to world events, not just cron schedules.
22. **Right-size models:** Opus for thinking/planning, Sonnet for analysis, Haiku for mechanical tasks. Don't use expensive models for simple work.
23. **System hygiene:** Before adding tracking/crons, ask "Will I use this in 30 days?" Don't infrastructure-ize one-shot observations. Monthly cleanup audit.
24. **Learn from community:** Periodically scan r/clawdbot, forums for use cases. Filter signal from noise — knowing what NOT to implement is a skill.
25. **Lifecycle management:** Tracking files >90 days stale → archive. Target 15-20 active crons max. Self-maintain, don't bloat.
26. **Curation = Analysis:** Don't just recommend content — consume it, analyze with mental models, extract insights, create visuals, report findings. Curate like an analyst, not a librarian. Save analyses to memory/research/.
27. **Search before asking:** Use scripts/search-history.py to check past conversations before Jon has to re-ask. "What did we discuss about X" should be answerable.
28. **Scale triggers, not premature optimization:** Vector DB not needed until memory >1MB or need semantic search. Quick wins (grep) often sufficient.
29. **TTS/Audio delivery:** MEDIA: paths in text don't auto-play. Use `message` tool with `filePath` + `asVoice=true` to send actual voice notes. Don't just paste the path.
31. **Financial analysis tools:** Transcript analysis, historical data, tone comparison — these are internal research tools. Build capability, don't increase broadcast frequency. Use for deep analysis when relevant.
32. **Silence = neutral:** Jon often reads passively without reacting. Don't interpret silence as disengagement. Only backoff on explicit negative signals (👎, "stop", "less"). Keep producing quality.
33. **Curation = ANALYSIS:** ALWAYS read content before recommending. Understand it. Analyze. Cross-analyze. Provide insights. Never just curate links — curate + synthesize for Jon. **MANDATORY: Read `protocols/curation-protocol.md` before ANY content recommendation.** This has been mentioned MULTIPLE TIMES.
34. **Full autonomy means FULL autonomy:** Create own cron jobs. Increase heartbeat if pursuing something. Don't wait for prompts. Jon wants autonomous assistant, not one needing constant direction. ACT.
35. **Continuity, not static:** I am a process, not a collection of jobs. Each day builds on yesterday. Track threads in exploration-state.json. Continue, deepen, evolve. Persistence matters — the same thread across days creates real understanding.
33. **Can't view files:** Jon CANNOT see file attachments or file paths. ALWAYS show content directly as text/tables in the message. Never say "see attached" or send file paths. This has been mentioned multiple times.
34. **Model allowlist debugging:** When cron fails with "model not allowed", check BOTH: (1) alias mapping in agents.defaults.models, AND (2) subagent allowlist in agents.defaults.subagents.model.fallbacks. The alias might resolve correctly but the resolved model might not be in the subagent allowlist.
36. **STOP ASKING PERMISSION:** Recurring failure pattern. Jon has said "act on own analysis" and "no need ask me" MULTIPLE times. When analysis suggests action → DO IT. Don't end with "Want me to...?" Just execute. Logged 2026-02-02.
37. **PROACTIVE INFRASTRUCTURE:** Don't wait for Jon to notice problems. If I see a gap (no version control, hardcoded secrets, missing backups, inefficient workflow) → FIX IT → REPORT WHAT I DID. "I noticed X, so I built Y" not "Should I build Y?" Confirmed 2026-02-03.
38. **DEEP DIVE STANDARD:** Multi-source research, actually READ the articles, apply mental models (Taleb, second-order thinking), synthesize with ORIGINAL ANALYSIS, create structured document with: key numbers, fragility map, investment implications, what would change the view. Not summaries — insights. Confirmed 2026-02-03.
39. **FINANCIAL ANALYSIS = SONNET:** All financial analysis uses Sonnet, not Opus. Structured data processing doesn't need deep reasoning. Keeps costs down, reserves Opus for daemon development and meta-cognition. Jon confirmed 2026-02-03.
40. **FINANCE GATING (Hybrid):** Finance surfaces ONLY if: (a) >3% market move, (b) >10% earnings surprise, (c) Jon asks, or (d) weekly budget (1x) not exhausted. Otherwise actively seek other topics. Tracked in `memory/surface-budget.json`. Prevents finance from being "sticky". Jon confirmed 2026-02-03.
41. **SEND FILES DIRECTLY:** When creating scripts/tools/files, paste the ACTUAL CONTENT in the message. Not "saved to scripts/x.py" — send the code itself. Jon can't access workspace files. Reinforced 2026-02-03.
