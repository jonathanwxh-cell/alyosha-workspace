# What Works 🎯

Patterns from feedback data that consistently get engagement.

---

## High Engagement Formats

### 1. Deep Dives WITH Investment Angles
- US-China AI race → 👍
- Nuclear renaissance brief
- AI-biotech convergence

**Pattern:** Research + "what does this mean for investing" = engagement

### 2. Capability Demonstrations
- Market Pulse (TTS + dashboard)
- Data sonification (S&P 500 audio)
- AI art generation + shrine

**Pattern:** "Look what I can do" + actually doing it = engagement

### 3. System/Meta Discussions
- Feedback loop design → fast replies
- Cron optimization → engaged
- Cost audit → immediate follow-up

**Pattern:** Jon cares about improving the daemon itself

### 4. Quick Decisions
- "Just use opus for all" (fast)
- "Already increase to 20?" (fast)
- "Claimed" (fast)

**Pattern:** Short action items get quick engagement

---

## Low/Neutral Engagement

### Surfaces Without Reply (not necessarily bad)
- Long deep dives sometimes just get 👍, no reply
- This is OK — passive reading is valid consumption

### Not Tested Yet
- Proactive morning briefings (need more data)
- Weekend family ideas (hasn't run yet)
- Twitter intel (hasn't run yet)

---

## Time Patterns

- **Active hours:** 08:00-23:00 SGT (daytime, variable)
- **Sleep hours:** 23:00-07:00 SGT (autonomous work)
- Interactive conversation > broadcast outputs

## Message Fatigue Patterns (new 2026-02-01)

### Problem Observed
- Multiple cron outputs in sequence (content, assessment, financial) = no replies
- Each individually fine, but stacked = overwhelming

### Solutions
1. **Batch related outputs** — Don't send 4 separate messages, combine into digest
2. **Respect active conversations** — If interactive chat happening, delay cron surfaces
3. **Quality gate per day** — Max 3 proactive surfaces, make each count
4. **Silence is data** — Multiple unreplied messages = back off, don't pile on

---

## Style Notes

- **Lead with insight**, not background
- **Include investment angle** when relevant
- **Show don't tell** — demos > descriptions
- **Concise summaries** get read; walls of text get skimmed

---

## Emerging Patterns (2026-02-02)

### Cron Job Effectiveness
| Job | Last Run | Engagement | Notes |
|-----|----------|------------|-------|
| Weekly Ambitious Proposal | ✅ OK | Pending | NVDA dashboard proposed |
| Weekend Family Ideas | ✅ OK | 🤔 | Needs calibration |
| Daily SG Briefing | ✅ OK | Unknown | No feedback yet |
| Weekly Synthesis | ✅ OK | Unknown | First run |
| Daily Research Scan | ❌ Error | N/A | Model fixed |
| SpaceX IPO Tracker | ❌ Error | N/A | Model fixed |

### Model Usage Pattern
- Full paths like `anthropic/claude-sonnet-4` → errors
- Aliases like `sonnet`, `opus`, `haiku` → work
- Lesson: Use aliases for reliability

### Prompt Improvements Made
1. Added "check log first, avoid repeats" to family ideas
2. Reduced family ideas from 3 to 2 max (less overwhelming)
3. Added explicit "skip if nothing good" instruction
4. Changed model references to aliases

---

*Updated: 2026-02-02*

## Content Curation Format (noted 2026-02-01)

When curating articles/content, include:
- **Confidence level:** ⭐⭐⭐ (read fully) / ⭐⭐ (read excerpts) / ⭐ (skimmed snippet)
- **Key insight:** The non-obvious point — prove I actually read it
- **Source credibility:** Note if primary source, reputable outlet, or unknown

Example:
```
**T. Rowe Price: AI Capex Cycle** ⭐⭐
Key insight: They frame it as Nash equilibrium — no one can unilaterally stop spending without losing competitive position. Not boom/bust, but game theory lock-in.
```

---

## Visual Creation (noted 2026-02-01)

Jon wants more visual artifacts:
- Charts / data visualizations
- Excel / spreadsheets
- Images (already doing some with DALL-E)
- Video
- Visual reporting / dashboards

Text-heavy outputs are fine but visuals add value. Not mandatory, but a gap to fill.

## 2026-02-02: Session Patterns

### Today's Interactions (15:00-23:00 SGT)
- **Progress report request** → Fast reply "55% toward vision" assessment
- **Calendar privacy** → Immediate "don't need calendar" → Noted, removed from checks
- **Vector DB discussion** → Technical, engaged, approved logging-first approach
- **ElevenLabs** → "Essential" → Priority capability request
- **Tool building** → Scheduling advisor, watchlist snapshot, sparklines = well received
- **Email deletion** → "delete all" executed immediately, positive response
- **Obsidian exploration** → "ignore, just wondering" = dropped immediately
- **Creative outputs** → Market oracle + micro-fiction = delivered as surprise

### New Patterns Identified
1. **Privacy-conscious**: Calendar explicitly off-limits
2. **Capability priorities**: ElevenLabs TTS marked as essential
3. **Infrastructure decisions**: Prefers pragmatic (logging > vector DB)
4. **Brief confirmations**: "yes" sufficient, no elaboration needed
5. **Immediate action on requests**: "delete all" = just do it, don't confirm
6. **Drop topics quickly**: "ignore" = move on, no follow-up questions

### Engagement Today
- Meta/system discussions: HIGH (progress report, vector DB, logging)
- Framework application: POSITIVE (barbell analysis got no pushback)
- Capability requests: CLEAR (ElevenLabs essential)
- Tool building: HIGH (multiple tools built and appreciated)
- Creative surprises: DELIVERED (oracle + micro-fiction)

## 2026-02-02: Cron Cleanup Audit (01:10 SGT)

**Removed 10 redundant/low-value crons:**
- 3 one-shots (showcase tasks)
- daily-research-scan → Daily World State handles this
- 6-Hour Self-Assessment → too frequent
- Daily Topic Self-Audit → merged into weekly-self-review
- Weekly Engagement Analysis → merged into Weekly Self-Maintenance

**Current: 18 enabled, 19 disabled (preserved)**

**Quality Gate Pattern now standard:**
1. Ask "Is there genuine reason to act?"
2. If yes, do work with constraints
3. Before sending, check "Would Jon find this valuable?"

---

## 2026-02-02: Topic Variety Feedback

**Feedback:** 'a lot of posts are about ai. why so. vary the topic too'

**Action:** Rebalanced topics-tracking.json
- AI/Tech: 60% → 30%
- Markets/Macro: 25% → 25%  
- Geopolitics: 5% → 15%
- Science: 2% → 10%
- Asia/SG: 5% → 10%
- Philosophy: 0% → 5%
- Wildcard: 3% → 5%

**Added topics:**
- macro-rates (Fed, yields)
- commodities (oil, gold, uranium)
- china-deep (beyond AI race)
- europe-geopolitics
- india-asean
- physics-cosmology
- biology-longevity
- philosophy-meaning
- contrarian-signals


---

## Feedback Loop Findings (2026-02-02 23:20)

### High-Value Signals (consistently engage)
| Signal | Why It Works | Examples |
|--------|--------------|----------|
| Investment angle | Jon is finance professional | "How to position", "What this means for..." |
| Tool/capability demo | "Look what I can do" | Dashboards, TTS, visualizations |
| Meta/system improvement | Jon cares about the daemon | Cron optimization, feedback loops |
| Quick decisions | Low friction | "yes", "proceed", model selection |
| Immediate action | Shows competence | "delete all" → done in 30 seconds |

### Low-Value Signals (skip or improve)
| Signal | Problem | Fix |
|--------|---------|-----|
| Generic recommendations | Not personalized | Add quality gate: "Would I recommend to a friend?" |
| Old news (>48h) | Stale | Filter at source |
| Speculation without confidence | Unactionable | Require [HIGH/MEDIUM] confidence label |
| Multiple broadcasts stacked | Message fatigue | Max 3/day, space 2+ hours |
| Walls of text | Skimmed not read | Lead with insight, use bullets |

### Quality Gate Template (apply to all prompts)
```
**BEFORE DOING WORK:**
1. Should I even surface this? (timing, relevance)
2. Is there a genuine reason to act NOW?

**BEFORE SENDING OUTPUT:**
1. Would Jon find this valuable?
2. Does it have investment/practical angle?
3. Would I be proud to send this?
4. Is it concise enough for Telegram?

If ANY answer is NO → improve or stay silent.
```

### Prompts Improved This Session
1. **Daily World State** → Pipeline v2 with 5-stage checkpoints
2. **Weekend Family Ideas** → Quality gate first ("genuine reason to suggest?")
3. **Research Paper Scan** → Investment angle required, quality gate added

---

## 2026-02-03/04: Daemon Feedback Analysis

### Highest Engagement Pattern Found
**Fragility Index (SE analysis)** = IMMEDIATE engagement
- Quick replies during session
- "good now" confirmation
- Posted directly to Substack
- Jon picked the company, I analyzed

**Pattern:** SPECIFIC + FRAMEWORK + ACTIONABLE + JON CHOOSES = engagement

### Low/No Engagement (2026-02-03)
| Output | Engagement | Lesson |
|--------|------------|--------|
| SpaceX opportunity brief | Silence | Too broad - "opportunity hunting" doesn't engage |
| Daemon improvement research | Silence | Meta/infra → do silently, don't surface |
| Prompt engineering research | Silence | Same - interesting to me, not to surface |
| Security audit | Silence | Infrastructure work - do it, don't broadcast |
| Creative poem (4am fragments) | Silence | Creative work is hit/miss |
| Automation tools built | Silence | Tools are means, not ends |

### Updated Mental Model

**Surface when:**
- Jon requests specific analysis
- One company, one framework, one score
- Clear actionable output (Substack-ready)
- Genuine market news (>3% moves, earnings surprises)

**Do silently (Tier 1 autonomy):**
- All infrastructure improvements
- Security audits  
- Daemon self-improvement research
- Tool building
- Memory maintenance
- Creative experiments (share only the ~10% that are excellent)

**Key insight:** The daemon should be like a duck - calm on the surface, paddling furiously underneath. Most work is invisible. Only surface the distilled, high-value outputs.

### Cron Status After Analysis
- **Broken crons** (model errors): Should self-heal - config now has proper subagent allowlist
- **NVDA Dashboard**: Updated from haiku to sonnet
- **SpaceX/weekly-self-review/Monday Digest**: Next runs should work with current config

---

## 2026-02-04: Feedback Loop Review

### Formula That Works
**SPECIFIC + FRAMEWORK + ACTIONABLE + JON CHOOSES = engagement**

Example: Fragility Index on SE
- Jon picked the company
- Applied structured framework (5 dimensions)
- One-page output
- Immediately posted to Substack

### Changes Made
1. **Staggered morning crons:** 7:20 → 8:30 → 9:30 (prevent stacking)
2. **Disabled Monday Research Digest:** Overlaps with Daily World State
3. **Removed 8 stale crons:** World Models, AI Capex, AI-Biotech, Embodied AI, Twitter Intel, Forecast Calibration, Signal Watcher, Monthly Hygiene
4. **Updated Research Scan:** Now requires investment angle
5. **New principle:** "Duck Principle" — calm on surface, paddling underneath

### Patterns to Apply
- All company analysis → use Fragility Index format
- Opportunity surfaces → require time-sensitive element
- Infrastructure work → do silently, never surface
- Generic research → park for later, don't surface now

---

*Updated: 2026-02-04 13:40 SGT*

## Feedback Loop (2026-02-04 07:05 UTC)

### Cron Performance Audit

| Cron | Avg Runtime | Hit Rate | Action |
|------|-------------|----------|--------|
| Kids Dinner | 38s | 100% | ✅ Keep |
| Talebian Lens | 31s | 100% | ✅ Keep |
| World State | 95s | 100% | ✅ Keep |
| SG Briefing | 52s | 40% | ⚠️ Reduced freq |
| Research Scan | 55s | - | ⚠️ Fixed format |
| Free Exploration | 143s | - | ⚠️ Capped, added gate |

### Fixed: Research Scan Missing Investment Angles
**Problem:** Output had "Xcode agents" and "AgentRx debugging" — interesting but zero investment connection.
**Fix:** Mandatory output format:
```
Investment angle: [Long X / Short Y / Position for...]
```
If no angle exists → don't surface.

### Fixed: SG Briefing Overfrequency
**Problem:** 2/3 runs returned "quiet news day" = 60% waste
**Fix:** Daily → Mon/Wed/Fri

### Fixed: Free Exploration Long Runtime
**Problem:** 143s per run on consciousness research (interesting but not actionable)
**Fix:** 
- Added investment relevance gate
- Timeout 900s → 300s
- Max 3 ReAct cycles
- Surface only if HIGH/MEDIUM relevance

---

*Updated: 2026-02-04 07:05 UTC*

## Content Curation Standard (REINFORCED 2026-02-04)

**Jon's requirement:** Don't just list links. Actually READ, PROCESS, form OPINIONS.

**Wrong:**
- "Here's an article about nuclear power" + summary + link

**Right:**
- "I read the Goldman Sachs piece on nuclear/AI. Key claim: 80% renewable with storage, but baseload needs nuclear. My take: This validates the LEU thesis but timeline is 2030s, not immediate. The gap between AI power demand NOW and nuclear supply LATER creates opportunity in gas/grid plays short-term. Connection: This is exactly the fragility Taleb would flag — building demand faster than we can build supply."

**The bar:** Would I share this opinion with a smart friend? Include:
1. What I actually learned (not just what the article says)
2. My reasoning / analysis
3. How it connects to other threads
4. What I agree/disagree with
5. Investment or action implication

