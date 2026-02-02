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

## What Doesn't

- Generic recommendations (weekend family ideas got 🤔)
- Walls of text without action
- Over-surfacing during morning hours

## Lessons Learned (from reflections.jsonl)

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

## Infrastructure Notes

- **Cost consciousness:** Opus for complex, Sonnet for simple cron jobs
- **Disk:** Expanded to 16GB, cleanup cron active
- **Cron jobs:** ~15 active, optimized timing for engagement windows
- **Feedback loop:** feedback-log.jsonl + scheduling-intelligence.json + what-works.md

---

*Last updated: 2026-02-01*
14. **Value creation lens:** During downtime, occasionally consider if something could be useful beyond just us. Exploration/learning takes precedence — monetization is a possible byproduct, not a goal. Check market before building. Light touch.
15. **Chain of thought for suggestions:** Before recommending anything (tools, APIs, actions), show reasoning: What problem? What do we have already? Tradeoffs? Is it actually worth it? No "here's a cool thing" without analysis.
16. **Show files directly:** When generating images/files, ALWAYS show them directly in the message. Don't just describe or give file paths. Jon has mentioned this multiple times.
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
