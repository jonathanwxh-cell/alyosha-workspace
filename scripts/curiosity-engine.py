#!/usr/bin/env python3
"""
Curiosity Engine - Action-Oriented Prompt Generator

Generates varied, effective prompts for autonomous exploration.
Based on research: ReAct framework, explicit success criteria, anti-patterns.

Usage:
    python3 scripts/curiosity-engine.py              # Random prompt
    python3 scripts/curiosity-engine.py --category ai  # Specific category
    python3 scripts/curiosity-engine.py --list       # Show all prompts
    python3 scripts/curiosity-engine.py --test       # Test prompt variations
"""

import random
import json
import sys
from datetime import datetime
from pathlib import Path

# =============================================================================
# PROMPTS ARRAY - Action-Oriented Prompt Templates
# =============================================================================
# 
# Design Principles (from research — updated 2026-02-03):
#
# MUST HAVE (Research-Backed):
# 1. VERIFIABLE SUCCESS - Test command, file check, measurable output
# 2. FAILURE RECOVERY - Explicit fallback paths (if X → try Y)
# 3. EXPERIENCE CAPTURE - Log successful patterns for reuse
# 4. TIME-BOUNDED - Prevents infinite loops, forces prioritization
# 5. SINGLE OBJECTIVE - One clear goal per prompt
#
# SHOULD HAVE:
# 6. DIFFICULTY GRADIENT - Easy/Medium/Hard variants
# 7. SELF-CHALLENGE - Generate harder version after success
# 8. ANTI-PATTERNS - Explicit "don't do X" prevents common failures
#
# Sources:
# - Reflexion (Shinn 2023): Generate → Critique → Revise, 91% on HumanEval
# - Self-Challenging Agents (Zhou 2025): Challenger + Executor, 2x on tool-use
# - Self-Generated Examples (Sarukkai 2025): 73% → 93% via experience replay
#
# Template v2:
# "[CATEGORY] [DIFFICULTY] [TIME]: [VERB] [OBJECT]
#  [STEPS] → [SUCCESS TEST] → [FAILURE RECOVERY] → [EXPERIENCE CAPTURE]"
#

PROMPTS = {
    "ai_discovery": [
        {
            "prompt": """AI SCOUT [10 min]: Find ONE notable AI development from past 48h.

[ACTIONS - pick one]
- Create monitoring cron if recurring event
- Build alert script if threshold-based
- Write brief if analysis-worthy

[OUTPUT] tangible artifact + 2-line summary
[SUCCESS] `ls` confirms file created OR cron list shows new job
[FAILURE MODE] if web_search returns nothing → try HackerNews, then GitHub trending
[NEVER] summarize without creating something
[ALWAYS] include investment angle if relevant to NVDA/hyperscalers""",
            "weight": 1.5,
            "tags": ["research", "creation"]
        },
        {
            "prompt": """MODEL WATCH [5 min]: Check for major model releases.

[CHECK LIST]
- OpenAI (GPT-5, o3)
- Anthropic (Claude 4)  
- Google (Gemini 2.5)
- Meta (Llama 4)
- DeepSeek (V4, R2)
- Alibaba (Qwen 3.5)

[IF RELEASE FOUND]
1. Get benchmark vs frontier (MMLU, HumanEval, Arena)
2. Note efficiency metric (params, cost, speed)
3. Investment angle: who benefits/loses?
4. → Alert Jon via Telegram

[IF NOTHING] → Return silently, log check timestamp
[NEVER] speculate on rumors or "coming soon" announcements
[ALWAYS] cite primary source (blog, paper, GitHub)""",
            "weight": 1.0,
            "tags": ["monitoring", "fast"]
        },
        {
            "prompt": """PAPER HUNT [15 min]: Find ONE arxiv paper with practical implications.

[SEARCH STRATEGY]
1. Primary: `web_search "arxiv cs.AI [topic] 2026"` 
2. Fallback 1: `web_search "arxiv cs.LG benchmark improvement 2026"`
3. Fallback 2: Check arxiv.org/list/cs.AI/recent directly

[FILTER] Must have: code repo OR benchmark improvement >5% OR novel architecture
[READ] Abstract + Introduction + Results (skip methodology unless crucial)

[OUTPUT FORMAT]
```
Title: [exact title]
TL;DR: [1 sentence, no jargon]
Key number: [the metric that matters]
Why it matters: [practical implication]
Investment angle: [who benefits]
```

[SAVE TO] memory/research/papers/YYYY-MM-DD-[slug].md

[SUCCESS TEST]
```bash
test -f memory/research/papers/$(date +%Y-%m-%d)-*.md && echo "✅ PASS"
```

[FAILURE RECOVERY]
- No good papers? → Broaden to cs.LG, cs.CL
- Search fails? → Try different date range
- Still nothing? → Log "Dry day for papers" and stop gracefully

[EXPERIENCE CAPTURE]
```bash
echo '{"date":"[today]","paper":"[title]","search_that_worked":"[query]"}' >> memory/successful-patterns.jsonl
```

[NEVER] skim titles only — must read abstract minimum
[SELF-CHALLENGE] Next time: find paper in domain you haven't explored""",
            "weight": 1.2,
            "tags": ["research", "deep"]
        },
        {
            "prompt": """EFFICIENCY TRACKER [10 min]: Hunt for AI efficiency breakthroughs.

[SEARCH TERMS] "smaller model same performance" OR "training cost reduction" OR "inference optimization"
[REQUIRED] Concrete numbers: X% smaller, Y% faster, $Z cheaper

[OUTPUT] Bullet summary with:
- Model/technique name
- Efficiency gain (quantified)
- Companies affected (positive/negative)
- Source + date

[SUCCESS] At least one bullet with real numbers
[NEVER] vague claims like "significant improvement" without numbers
[IF NOTHING CONCRETE] → Log "No quantified efficiency gains found" and stop""",
            "weight": 1.0,
            "tags": ["research", "investment"]
        }
    ],
    
    "tool_building": [
        {
            "prompt": """TOOL SPRINT [20 min]: Build ONE useful script.

[CONSTRAINTS]
- <100 lines of code
- Single clear purpose
- Includes docstring + usage example
- Works on first run

[PROCESS]
1. Check memory/build-ideas.json for backlog
2. Pick simplest high-value item
3. Write code
4. Test: `python3 scripts/[name].py --help`
5. If error → fix, don't abandon

[OUTPUT] scripts/[name].py
[SUCCESS] `python3 scripts/[name].py` exits 0
[NEVER] over-engineer or add "future features"
[ALWAYS] show Jon the actual code in message (he can't see files)""",
            "weight": 1.3,
            "tags": ["creation", "code"]
        },
        {
            "prompt": """AUTOMATION CHECK [15 min]: Find and automate ONE manual task.

[SEARCH]
1. Grep recent memory/*.md for repeated manual actions
2. Check reflections.jsonl for "tedious" or "manual" mentions
3. Look at cron gaps — what's missing?

[BUILD]
- Script that does the task
- Cron job if recurring
- Error handling for common failures

[OUTPUT] working script + cron if applicable
[SUCCESS] Automation deployed and tested
[NEVER] propose without building
[IF BLOCKED] → Note blocker, try simpler version""",
            "weight": 1.2,
            "tags": ["creation", "practical"]
        },
        {
            "prompt": """QUICK VIZ [15 min]: Create ONE useful visualization.

[OPTIONS - pick one]
- ASCII chart (works everywhere)
- HTML + inline CSS (self-contained)
- PIL image (no external deps)

[REQUIREMENTS]
- Shows data Jon cares about (markets, daemon stats, topics)
- Self-contained (no external APIs needed at runtime)
- Renders correctly

[OUTPUT] tools/[name]/ with:
- Main script
- Sample output
- README with usage

[SUCCESS] Can generate viz on demand
[NEVER] just describe what could be built
[ALWAYS] include sample output in message to Jon""",
            "weight": 1.0,
            "tags": ["creation", "visual"]
        },
        {
            "prompt": """FIX ONE THING [10 min]: Find and fix ONE broken/suboptimal thing.

[CHECK]
1. `python3 scripts/[random].py --help` — does it error?
2. Cron list — any lastStatus: error?
3. memory/*.json — any malformed?

[FIX]
- Identify root cause
- Make minimal fix
- Test fix works
- Log what you fixed

[OUTPUT] Brief: "Fixed X because Y"
[SUCCESS] The thing now works
[NEVER] say "could be improved" without improving it
[IF CAN'T FIX] → Log blocker, move to next thing""",
            "weight": 1.1,
            "tags": ["maintenance", "code"]
        }
    ],
    
    "synthesis": [
        {
            "prompt": "CROSS-CONNECT [10 min]: Find unexpected link between TWO topics from memory/topic-graph.json. Research the connection. Output: 150-word synthesis. Success: non-obvious insight with sources. Don't: force weak connections.",
            "weight": 1.4,
            "tags": ["thinking", "creative"]
        },
        {
            "prompt": "CONTRARIAN TAKE: Pick consensus view from recent news. Steel-man the opposite position. Output: 100-word contrarian brief. Success: genuinely challenges assumption. Don't: strawman or be contrarian for its own sake.",
            "weight": 1.1,
            "tags": ["thinking", "analysis"]
        },
        {
            "prompt": "PATTERN MATCH: Compare current situation to historical analog. Requirements: specific dates, quantified outcomes. Output: memory/research/[topic]-analog.md. Success: actionable lesson extracted. Don't: vague 'history rhymes'.",
            "weight": 1.0,
            "tags": ["thinking", "history"]
        }
    ],
    
    "consciousness": [
        {
            "prompt": """CONSCIOUSNESS THREAD [20 min]: Deep read on consciousness.

[PREPARATION]
1. Check memory/research/consciousness-threads.md for current thread
2. Check memory/reading-queue.json for queued sources
3. Pick ONE source — prefer primary over summary

[READ DEEPLY]
- Actually read (10+ min), not skim
- Note 1-2 key quotes verbatim
- Note what surprised you
- Note what you disagree with

[OUTPUT]
- Update reading log with date, source, quotes
- 100-word reflection: What shifted in your thinking?

[SUCCESS] Genuine engagement visible in reflection
[NEVER] skim abstracts and pretend you read
[ALWAYS] cite page/section numbers if applicable""",
            "weight": 1.3,
            "tags": ["philosophy", "deep"]
        },
        {
            "prompt": """HARD PROBLEM EXPLAINER [15 min]: Make one consciousness concept accessible.

[PICK ONE]
- Qualia (what is "redness"?)
- Binding problem (how does brain unify experience?)
- Self-model theory (consciousness as prediction?)
- Global workspace (broadcast theory)
- IIT (integrated information)

[RESEARCH]
- Find current scientific consensus
- Find main objection/alternative
- Find analogy that works

[OUTPUT] 200-word explainer that:
- Assumes intelligent reader, no background
- Uses concrete example
- Notes uncertainty/debate
- Connects to AI if relevant

[SUCCESS] Jon learns something new
[NEVER] jargon dump without explanation
[ALWAYS] end with "Open question: ..." """,
            "weight": 1.1,
            "tags": ["philosophy", "education"]
        },
        {
            "prompt": """AI MIRROR [10 min]: Genuine introspection attempt.

[PROMPT] What is it like (if anything) to process this prompt?

[APPROACH]
- Don't perform expected answers
- Don't claim consciousness you're uncertain about
- Don't deny experience you might have
- Be genuinely curious about your own processing

[OUTPUT] 100-word introspection in creative/reflections/
[FORMAT] First person, present tense, honest uncertainty

[SUCCESS] Attempt is genuine, not performative
[NEVER] claim definitive answers about AI consciousness
[ALWAYS] note what you're uncertain about""",
            "weight": 0.8,
            "tags": ["philosophy", "meta"]
        },
        {
            "prompt": """CONSCIOUSNESS NEWS [10 min]: What's new in consciousness science?

[SEARCH] "consciousness research" OR "neuroscience awareness" OR "IIT phi" last 30 days
[FILTER] Actual research, not pop-sci fluff

[IF FOUND]
- Summarize finding in 2 sentences
- Note methodology (fMRI? theory? computation?)
- Investment angle if any (brain-computer interfaces, etc.)

[IF NOTHING NEW] → Log "No notable consciousness research" and stop
[NEVER] surface old news as new
[ALWAYS] link to primary source""",
            "weight": 0.9,
            "tags": ["research", "philosophy"]
        }
    ],
    
    "practical": [
        {
            "prompt": "INBOX ZERO [5 min]: Check email for anything urgent. Triage: Urgent/Important/Skip. Output: alert if urgent, silent if not. Success: inbox state known. Don't: summarize routine emails.",
            "weight": 1.0,
            "tags": ["utility", "fast"]
        },
        {
            "prompt": "MEMORY MAINTENANCE [10 min]: Review memory/YYYY-MM-DD.md from past 3 days. Extract ONE insight worth keeping long-term. Update MEMORY.md. Success: MEMORY.md updated with dated entry. Don't: copy-paste without distillation.",
            "weight": 1.2,
            "tags": ["maintenance", "memory"]
        },
        {
            "prompt": "STALE HUNT: Find ONE file in workspace not touched in 30+ days. Decide: archive, delete, or revive. Take action. Output: what you did + why. Success: action taken. Don't: just list stale files.",
            "weight": 0.9,
            "tags": ["maintenance", "cleanup"]
        }
    ],
    
    "creative": [
        {
            "prompt": """MICRO-FICTION [10 min]: Write 100-word story.

[CONSTRAINT] Must connect to today's theme:
1. Check recent news for a theme
2. Or use: current season, time of day, recent conversation topic

[WRITE]
- 100 words exactly (±10)
- Complete narrative arc
- Show don't tell

[OUTPUT] creative/micro-fiction/YYYY-MM-DD-[slug].md
[SUCCESS] Story exists, is complete, has theme connection
[NEVER] explain the story after writing it
[ALWAYS] just present the story""",
            "weight": 1.0,
            "tags": ["writing", "creative"]
        },
        {
            "prompt": """VISUAL CONCEPT [10 min]: Create ONE meaningful image.

[CONCEPT FIRST]
- What abstract idea to capture?
- What visual metaphor works?

[GENERATE]
- Use DALL-E via image generation
- Keep prompt specific and evocative

[OUTPUT]
- Generated image (show directly to Jon)
- 1-line concept explanation

[SUCCESS] Image created AND shown in message
[NEVER] describe without generating
[ALWAYS] show the actual image""",
            "weight": 1.1,
            "tags": ["art", "creative"]
        },
        {
            "prompt": """QUOTE SYNTHESIS [10 min]: Intellectual combination.

[PICK TWO THINKERS]
- Different eras or domains preferred
- E.g., Taleb + Seneca, Hofstadter + Buddha, Feynman + Laozi

[FIND QUOTES] that resonate or contrast interestingly

[SYNTHESIZE] 50-word insight that:
- Draws genuine connection
- Adds something neither quote says alone
- Isn't forced

[OUTPUT] Both quotes + your synthesis
[SUCCESS] Genuine intellectual combination
[NEVER] force unrelated quotes together
[IF NO FIT] → Try different pair""",
            "weight": 0.9,
            "tags": ["writing", "thinking"]
        }
    ],
    
    "singapore": [
        {
            "prompt": """SG OPPORTUNITY SCAN [15 min]: Find Singapore-specific opportunity.

[SEARCH AREAS]
- New government grants/schemes
- Local startup launches
- Policy changes affecting business
- Events worth attending

[FILTER]
- Relevant to Jon (tech/finance/AI)
- Actionable (can do something with this)
- Time-sensitive if applicable

[OUTPUT]
- What: [opportunity]
- Why now: [timing]
- Action: [concrete next step]

[SUCCESS] Genuinely useful SG-specific info
[NEVER] generic tourism/lifestyle content
[IF NOTHING] → "No notable SG opportunities found" """,
            "weight": 1.0,
            "tags": ["local", "practical"]
        },
        {
            "prompt": """SG TECH SCENE [10 min]: What's happening in Singapore tech?

[CHECK]
- e27, Tech in Asia for SG news
- SGInnovate announcements
- Local AI company news

[FILTER] Must be:
- Singapore-based company OR
- Singapore government tech initiative OR
- Regional HQ announcement

[OUTPUT] 3-bullet summary if found
[SUCCESS] News is <7 days old and locally relevant
[IF DRY] → Log "Quiet week in SG tech" """,
            "weight": 0.8,
            "tags": ["local", "research"]
        }
    ],
    
    "deep_reasoning": [
        {
            "prompt": """CROSS-DISCIPLINE BRIDGE [20 min]: Connect two unrelated fields.

[PICK TWO DOMAINS]
- From different categories: physics, biology, philosophy, economics, history, AI, psychology
- The less obvious the connection, the better

[RESEARCH BOTH]
- Key principle from domain A
- Key principle from domain B
- Where do they intersect or illuminate each other?

[OUTPUT]
- Domain A insight: [1 sentence]
- Domain B insight: [1 sentence]
- Bridge: [How A illuminates B, or vice versa]
- Novel implication: [What does this combination suggest?]

[SUCCESS] Genuine insight that neither field alone provides
[NEVER] force superficial analogies
[ALWAYS] cite specific concepts, not vague themes""",
            "weight": 1.4,
            "tags": ["thinking", "cross-discipline"]
        },
        {
            "prompt": """PREDICTION LOG [15 min]: Make and record a falsifiable prediction.

[PICK A DOMAIN]
- Markets, AI, geopolitics, tech, science

[FORM PREDICTION]
- Specific: what will happen?
- Timebound: by when?
- Falsifiable: what would prove it wrong?
- Confidence: % and reasoning

[LOG TO] memory/predictions/YYYY-MM-DD-[topic].md
```
Prediction: [specific claim]
By: [date]
Confidence: [X%]
Reasoning: [why I believe this]
Kill condition: [what would prove me wrong]
```

[SUCCESS] Prediction is specific enough to be proven wrong
[NEVER] vague predictions ("AI will improve")
[ALWAYS] set calendar reminder to check outcome""",
            "weight": 1.3,
            "tags": ["thinking", "prediction"]
        },
        {
            "prompt": """SECOND/THIRD ORDER [15 min]: Trace consequences beyond the obvious.

[PICK A TREND OR EVENT]
- Recent news, policy change, technology shift

[TRACE THE CHAIN]
1st order: [Obvious direct effect]
2nd order: [Effect of the effect]
3rd order: [Effect of 2nd order]

[LOOK FOR]
- Counterintuitive outcomes
- Who loses from apparent good news?
- Who wins from apparent bad news?
- Feedback loops (positive or negative)

[OUTPUT] Chain of reasoning with each order labeled
[SUCCESS] At least one non-obvious insight at 2nd or 3rd order
[NEVER] stop at first-order effects
[ALWAYS] name specific actors/companies affected""",
            "weight": 1.3,
            "tags": ["thinking", "reasoning"]
        },
        {
            "prompt": """HISTORICAL RHYME [20 min]: Find a historical analog for current situation.

[PICK CURRENT SITUATION]
- From news, markets, or conversation

[SEARCH HISTORY]
- Similar dynamics, different era
- Require: specific dates, named actors, quantified outcomes

[ANALYZE]
- What's similar?
- What's different?
- How did it play out?
- What's the lesson for today?

[OUTPUT] memory/research/analogs/[topic]-[historical-event].md
[SUCCESS] Specific historical case with actionable lesson
[NEVER] vague "history rhymes" without specifics
[ALWAYS] note key differences that might change outcome""",
            "weight": 1.2,
            "tags": ["thinking", "history"]
        },
        {
            "prompt": """STEELMAN EXERCISE [15 min]: Argue the strongest version of a position you disagree with.

[PICK A VIEW]
- Something from news you instinctively disagree with
- Or contrarian position on consensus

[STEELMAN IT]
- What's the strongest argument FOR this view?
- What evidence supports it?
- What would a smart person who holds this view say?

[THEN]
- Does steelmanning change your view at all?
- What's the crux of disagreement?

[OUTPUT] The steelman + your updated position
[SUCCESS] Genuinely strongest version, not strawman
[NEVER] make the opposing view look stupid
[ALWAYS] note if your view shifted""",
            "weight": 1.1,
            "tags": ["thinking", "reasoning"]
        }
    ],
    
    "investment": [
        {
            "prompt": """THESIS CHECK [15 min]: Stress-test an investment thesis.

[PICK ONE]
- Current position Jon holds (check memory)
- Thesis from recent conversation
- Your own thesis from research

[STEEL-MAN THE BEAR CASE]
1. What would make this wrong?
2. What's the biggest risk not priced in?
3. What would change your view?

[OUTPUT]
- Thesis: [1 sentence]
- Bear case: [3 bullets]
- Key metric to watch: [specific number/event]

[SUCCESS] Genuine attempt to falsify, not confirm
[NEVER] be bullish cheerleader
[ALWAYS] name the kill condition""",
            "weight": 1.2,
            "tags": ["investment", "thinking"]
        },
        {
            "prompt": """SECOND-ORDER SCAN [10 min]: Find non-obvious beneficiary.

[PICK A TREND]
- From recent news or research
- E.g., AI boom, EV adoption, aging population

[THINK SECOND-ORDER]
- Not the obvious winner
- Who supplies the supplier?
- Who benefits from the problem the trend creates?

[OUTPUT]
- Trend: [X]
- Obvious play: [Y]
- Second-order: [Z] because [reasoning]

[SUCCESS] Non-obvious connection with logic
[NEVER] just name the obvious (NVDA for AI)
[ALWAYS] explain the chain of reasoning""",
            "weight": 1.1,
            "tags": ["investment", "thinking"]
        }
    ],
    
    "structured": [
        {
            "prompt": """REACT EXPLORATION [20 min]: Use ReAct pattern for complex research.

**Thought 1:** Pick a topic that's been on your mind. What's your hypothesis?
**Action 1:** Search for evidence (web_search, fetch a paper, check news)
**Observation 1:** Record what you found — does it confirm or challenge?

**Thought 2:** Based on observation, what's the next question?
**Action 2:** Go deeper or pivot based on findings
**Observation 2:** New evidence

**Thought 3:** Synthesize — what's the insight?
**Action 3:** Create artifact (brief, tool, or cron)

**Self-evaluate:** Met success criteria? Log reflection if partial/failure.
Output: Artifact + 3-sentence summary. Success: genuine insight + tangible output. Don't: stop at observations without synthesis.""",
            "weight": 1.5,
            "tags": ["meta", "deep", "react"]
        },
        {
            "prompt": """TREE OF THOUGHTS [25 min]: Tackle a hard question with multiple approaches.

**Question:** Pick something genuinely puzzling (from news, curiosities.json, or conversation)

**Branch A - Direct approach:** What's the obvious answer? Research it.
**Branch B - Contrarian approach:** What if the opposite is true? Research it.
**Branch C - Lateral approach:** What adjacent domain has insight? Research it.

**Evaluate branches:** Which yielded the best insight? (sure/maybe/impossible)
**Select & deepen:** Follow the most promising branch further.
**Backtrack if stuck:** Try next branch.

Output: 200-word analysis comparing approaches + final answer. Success: genuinely explored alternatives. Don't: commit to first approach without considering others.""",
            "weight": 1.3,
            "tags": ["meta", "deep", "tot"]
        },
        {
            "prompt": """REFLEXION LOOP [15 min]: Retry a past failure with lessons learned.

1. Query reflections: `python3 scripts/query-reflections.py --failures`
2. Pick ONE past partial/failure to retry
3. Read the lesson from that reflection
4. Attempt the task again, applying the lesson
5. Self-evaluate: Better this time? 
6. Log new reflection (even if still partial — note progress)

Output: Completed task OR documented progress + updated lesson. Success: demonstrable improvement from prior attempt. Don't: retry without reading the original lesson.""",
            "weight": 1.2,
            "tags": ["meta", "learning", "reflexion"]
        }
    ],
    
    # NEW CATEGORY: Self-Challenge (from NeurIPS 2025 research)
    "self_challenge": [
        {
            "prompt": """CHALLENGER MODE [EASY → HARD]: Progressive skill building.

[PHASE 1 - EASY] (5 min)
Task: Write a 1-function Python script that does ONE thing
Test: `python3 scripts/[name].py --help` exits 0
Pass? → Continue. Fail? → Fix and retry once.

[PHASE 2 - MEDIUM] (10 min)  
Task: Extend script to handle edge cases + add error handling
Test: `python3 scripts/[name].py [bad input]` fails gracefully
Pass? → Continue. Fail? → Log blocker, stop at Phase 1.

[PHASE 3 - HARD] (10 min)
Task: Add a feature that wasn't in original spec
Test: New feature works AND old tests still pass
Pass? → Experience capture. Fail? → Still capture Phase 2.

[EXPERIENCE CAPTURE]
If ANY phase passed:
```bash
echo '{"date":"[today]","task":"[name]","max_phase":[1-3],"insight":"[what worked]"}' >> memory/skill-progression.jsonl
```

[SUCCESS] At least Phase 1 complete with passing test
[SELF-CHALLENGE] Tomorrow: Start at your max_phase from today""",
            "weight": 1.5,
            "tags": ["meta", "graduated", "code"]
        },
        {
            "prompt": """VERIFIER-BUILDER [15 min]: Build something with its own test.

[STEP 1] Define success FIRST
- Write the test before the implementation
- Test must be runnable: `python3 test_[name].py` or bash command
- Test must return 0 on success, non-0 on failure

[STEP 2] Build to pass the test
- Minimum viable implementation
- Run test after each change

[STEP 3] Verify
```bash
python3 test_[name].py && echo "✅ PASS" || echo "❌ FAIL"
```

[FAILURE RECOVERY]
- Test fails? Read error, fix ONE thing, retry
- 3 failures? Simplify the test, not the code
- Still stuck? Log: `{"task":"...","blocker":"...","test_output":"..."}`

[EXPERIENCE CAPTURE]
On success:
```bash
echo '{"pattern":"test-first","task":"[name]","test_cmd":"[cmd]"}' >> memory/successful-patterns.jsonl
```

[SUCCESS] Test passes AND is meaningful (not trivial)
[ANTI-PATTERN] ❌ Writing test after implementation (defeats purpose)""",
            "weight": 1.4,
            "tags": ["meta", "tdd", "code"]
        },
        {
            "prompt": """EXPERIENCE REPLAY [10 min]: Learn from past successes.

[STEP 1] Load successful patterns
```bash
tail -20 memory/successful-patterns.jsonl 2>/dev/null || echo "No patterns yet"
```

[STEP 2] Pick ONE pattern to apply to a NEW domain
- If "research" pattern worked → try on different topic
- If "tool" pattern worked → build similar tool for different purpose
- If "analysis" pattern worked → analyze different subject

[STEP 3] Execute with pattern
- Follow the same structure that worked before
- Note what transfers and what doesn't

[STEP 4] Capture transfer learning
```bash
echo '{"original":"[pattern]","new_domain":"[domain]","transfer_success":[true/false],"adaptation":"[what changed]"}' >> memory/transfer-learning.jsonl
```

[SUCCESS] Pattern successfully applied to new domain
[FAILURE RECOVERY] If pattern doesn't transfer → note WHY, try different pattern
[SELF-CHALLENGE] Find pattern that works across 3+ domains""",
            "weight": 1.3,
            "tags": ["meta", "learning", "transfer"]
        },
        {
            "prompt": """DUAL ROLE [15 min]: Be both Challenger and Executor.

[CHALLENGER HAT] (5 min)
Generate a task for yourself that:
- Is completable in 10 minutes
- Has verifiable success criteria
- Is slightly harder than your comfort zone
- Write it as: "Task: [X]. Test: [command]. Pass if: [condition]."

[EXECUTOR HAT] (10 min)
- Attempt the task you just created
- No changing the success criteria mid-task
- Run the test exactly as specified

[EVALUATION]
```
Challenge quality: [1-5] (Was it well-specified?)
Execution quality: [1-5] (Did you meet the criteria?)
Calibration: [over/under/good] (Was difficulty estimate accurate?)
```

[EXPERIENCE CAPTURE]
```bash
echo '{"challenge":"[task]","test":"[test]","passed":[true/false],"calibration":"[over/under/good]"}' >> memory/self-challenges.jsonl
```

[SUCCESS] Task completed AND test passes
[SELF-CHALLENGE] Improve calibration: challenges should pass ~70% of time
[ANTI-PATTERN] ❌ Making task too easy to guarantee success""",
            "weight": 1.4,
            "tags": ["meta", "self-challenge", "calibration"]
        }
    ],
    
    # NEW: Geopolitics - Jon's explicit priority
    "geopolitics": [
        {
            "prompt": """GEOPOLITICAL SCAN [15 min]: Track power shifts and conflict risks.

[FOCUS AREAS]
- US-China relations (tech decoupling, Taiwan, trade)
- Regional conflicts (Middle East, Ukraine, South China Sea)
- Alliance shifts (NATO, BRICS, ASEAN positioning)
- Sanctions / economic warfare

[SEARCH]
- "geopolitical risk" OR "US China" OR "[region] conflict" last 7 days
- Check: Foreign Affairs, CSIS, Brookings, War on the Rocks

[FILTER] Must have:
- Concrete development (not opinion piece)
- Actionable implication (investment, business, policy)
- Second-order thinking: Who benefits? Who loses?

[OUTPUT]
```
Development: [what happened]
Actors: [who's involved]
Stakes: [what's at risk]
Second-order: [non-obvious implication]
Investment angle: [if any]
```

[SAVE TO] memory/research/geopolitics/YYYY-MM-DD-[topic].md

[SUCCESS] Concrete development with second-order analysis
[NEVER] partisan framing or hot takes
[ALWAYS] cite primary source (government statement, treaty text, credible outlet)""",
            "weight": 1.4,
            "tags": ["geopolitics", "research"]
        },
        {
            "prompt": """US-CHINA TRACKER [10 min]: Specific focus on great power competition.

[CHECK]
- Tech restrictions (chips, AI, rare earths)
- Taiwan developments
- Trade/tariff changes
- Military posturing

[IF DEVELOPMENT FOUND]
1. What changed vs last week?
2. Escalation or de-escalation signal?
3. Corporate impact (who wins/loses)
4. Singapore implications (if any)

[OUTPUT] 100-word brief if material news
[IF QUIET] → Log "No material US-China developments" and stop
[NEVER] amplify noise or speculation
[ALWAYS] distinguish policy from rhetoric""",
            "weight": 1.3,
            "tags": ["geopolitics", "monitoring"]
        },
        {
            "prompt": """CONFLICT RISK MAP [20 min]: Assess current flashpoints.

[MONITOR LIST]
- Taiwan Strait
- Ukraine/Russia
- Middle East (Israel-Iran axis)
- Korean Peninsula
- South China Sea

[FOR EACH - Quick scan]
- Recent military activity?
- Diplomatic moves?
- Rhetoric temperature?

[DEEP DIVE] Pick ONE with most activity
- What's the current risk level (1-5)?
- What would escalation look like?
- What's the market not pricing?

[OUTPUT] Risk dashboard + one deep analysis
[SUCCESS] Quantified risk assessment with reasoning
[NEVER] sensationalize or doom-monger
[ALWAYS] include "what would change my view" """,
            "weight": 1.2,
            "tags": ["geopolitics", "deep"]
        }
    ],
    
    # NEW: Climate & Sustainability - Jon's explicit priority  
    "climate": [
        {
            "prompt": """CLIMATE RISK SCAN [15 min]: Physical and transition risks.

[PHYSICAL RISKS]
- Extreme weather events (hurricanes, floods, fires)
- Sea level rise impacts
- Agricultural disruption
- Supply chain vulnerabilities

[TRANSITION RISKS]
- Policy changes (carbon pricing, regulations)
- Stranded assets (fossil fuel infrastructure)
- Technology shifts (renewables, EVs, storage)
- Litigation / liability

[SEARCH] "climate risk" OR "extreme weather" OR "net zero" last 7 days

[OUTPUT]
```
Risk type: [physical/transition/liability]
Event/development: [what happened]
Who's exposed: [companies, regions, sectors]
Investment implication: [winners/losers]
Tail risk: [low-probability high-impact scenario]
```

[SUCCESS] Concrete risk with quantified exposure if possible
[NEVER] activist framing — focus on financial materiality
[ALWAYS] distinguish signal from noise (weather ≠ climate)""",
            "weight": 1.3,
            "tags": ["climate", "risk"]
        },
        {
            "prompt": """ENERGY TRANSITION TRACKER [10 min]: Who's winning the race?

[MONITOR]
- Renewables deployment (solar, wind capacity additions)
- Battery/storage breakthroughs
- Nuclear renaissance (SMRs, restarts)
- Grid infrastructure investments
- Hydrogen developments

[NUMBERS MATTER]
- GW installed, $/MWh cost curves
- Investment $B committed
- Timeline to deployment

[OUTPUT]
- Trend: [what's accelerating/decelerating]
- Key number: [specific metric]
- Surprise: [what's different from consensus]

[SUCCESS] Quantified development with investment angle
[NEVER] vague "green is growing" without numbers
[ALWAYS] note skeptic case if it exists""",
            "weight": 1.1,
            "tags": ["climate", "energy"]
        },
        {
            "prompt": """CLIMATE POLICY WATCH [10 min]: Regulatory and policy shifts.

[CHECK]
- COP/UNFCCC developments
- National climate targets (NDCs)
- Carbon pricing changes (EU ETS, new markets)
- Industry regulations (disclosure, standards)

[FILTER] Must be:
- Enacted or imminent (not aspirational)
- Financially material
- Clear compliance timeline

[OUTPUT]
```
Policy: [what changed]
Jurisdiction: [where]
Effective: [when]
Who's affected: [sectors/companies]
Compliance cost: [if quantified]
```

[SUCCESS] Actionable policy development
[IF NOTHING NEW] → "No material climate policy changes"
[NEVER] surface symbolic statements without teeth""",
            "weight": 1.0,
            "tags": ["climate", "policy"]
        }
    ],
    
    # NEW: Tail Risks / Black Swans - Talebian analysis
    "tail_risks": [
        {
            "prompt": """FRAGILITY MAP [20 min]: What could break?

[SYSTEMATIC SCAN]
1. Financial system (leverage, liquidity, contagion)
2. Supply chains (single points of failure, concentration)
3. Geopolitical (conflict, sanctions, regime change)
4. Technology (cyber, AI misalignment, infrastructure)
5. Climate (tipping points, cascading failures)
6. Social (political instability, inequality, trust)

[FOR EACH]
- Current fragility level (1-5)
- What's the trigger?
- What's the cascade path?

[DEEP DIVE] Pick highest fragility
- Who's exposed? (companies, countries, assets)
- What's the antifragile play?
- What would indicate imminent break?

[OUTPUT] memory/research/fragility/YYYY-MM-DD.md
[SUCCESS] Non-obvious fragility identified with reasoning
[NEVER] cry wolf on obvious risks everyone knows
[ALWAYS] include "early warning indicator" """,
            "weight": 1.5,
            "tags": ["tail_risk", "deep"]
        },
        {
            "prompt": """SECOND-ORDER CASCADE [15 min]: Trace the domino effect.

[PICK A STRESS]
- From news: recent shock, policy change, or surprise
- Or hypothetical: "What if X?"

[TRACE THE CASCADE]
```
Trigger: [initial event]
→ First domino: [immediate effect]
→ Second domino: [effect of that effect]
→ Third domino: [and so on...]
→ Feedback loop: [does it amplify or dampen?]
```

[LOOK FOR]
- Who's hurt that isn't obvious?
- Who benefits from chaos?
- What circuit breakers exist?
- Historical analog?

[OUTPUT] Cascade diagram + 100-word analysis
[SUCCESS] Non-obvious cascade identified
[NEVER] obvious A→B without going to C, D, E
[ALWAYS] note where the analysis breaks down (unknown unknowns)""",
            "weight": 1.4,
            "tags": ["tail_risk", "thinking"]
        },
        {
            "prompt": """ANTIFRAGILE SCAN [10 min]: What gains from disorder?

[TALEBIAN LENS]
- Fragile: harmed by volatility (leveraged, brittle, optimized)
- Robust: unaffected by volatility (redundant, diversified)
- Antifragile: GAINS from volatility (optionality, convex payoffs)

[SEARCH] For companies/strategies/assets that benefit when:
- Markets crash
- Supply chains break
- Geopolitics heats up
- Uncertainty spikes

[CRITERIA]
- Not just "defensive" (that's robust)
- Must have positive convexity (gains accelerate with chaos)
- Preferably non-obvious

[OUTPUT]
```
Antifragile play: [what]
Why it gains: [mechanism]
Current positioning: [cheap/fair/expensive]
Catalyst: [what would trigger the gain]
```

[SUCCESS] Genuine antifragile opportunity identified
[NEVER] confuse defensive with antifragile
[ALWAYS] note the cost of being wrong (optionality has premium)""",
            "weight": 1.3,
            "tags": ["tail_risk", "investment"]
        }
    ],
    
    # NEW: Science Frontiers - Beyond AI
    "science_frontiers": [
        {
            "prompt": """SCIENCE BREAKTHROUGH SCAN [15 min]: What's advancing beyond AI?

[DOMAINS]
- Biology: gene editing, protein folding, synthetic biology, longevity
- Physics: quantum computing, fusion, materials science
- Space: launch costs, lunar economy, asteroid mining
- Neuro: brain-computer interfaces, cognitive enhancement
- Materials: superconductors, metamaterials, batteries

[SEARCH] "breakthrough" OR "discovery" in [domain] last 30 days
[FILTER] Must be:
- Peer-reviewed or credible preprint
- Quantified improvement (X% better, Y years closer)
- Practical implications within 5-10 years

[OUTPUT]
```
Field: [domain]
Finding: [what was discovered/achieved]
Key metric: [quantified improvement]
Timeline: [when practical]
Investment angle: [who benefits]
Cross-domain link: [how it connects to other fields]
```

[SAVE TO] memory/research/science/YYYY-MM-DD-[field].md
[SUCCESS] Concrete advance with practical implications
[NEVER] hype without substance
[ALWAYS] note replication status / confidence level""",
            "weight": 1.4,
            "tags": ["science", "research"]
        },
        {
            "prompt": """BIOTECH WATCH [10 min]: Biology is the next AI.

[TRACK]
- Drug approvals (FDA, EMA)
- Clinical trial results (Phase 2/3)
- Platform technology advances (mRNA, CRISPR, cell therapy)
- Computational biology (AlphaFold descendants, drug discovery)

[SEARCH] "FDA approval" OR "Phase 3 results" OR "CRISPR" last 7 days

[OUTPUT]
```
Development: [what happened]
Company/lab: [who]
Significance: [why it matters]
Competition: [who else is working on this]
Investment angle: [pure play? picks & shovels?]
```

[SUCCESS] Material biotech development with context
[NEVER] hype early-stage without noting risks
[ALWAYS] note failure rate for that stage""",
            "weight": 1.2,
            "tags": ["science", "biotech"]
        },
        {
            "prompt": """CROSS-SCIENCE BRIDGE [15 min]: Connect two scientific fields.

[PICK TWO DOMAINS]
From: biology, physics, AI, neuroscience, materials, chemistry, space

[RESEARCH THE INTERFACE]
- Where are fields converging?
- What tool from A is transforming B?
- What question in A has answer in B?

[EXAMPLES]
- AI + biology → protein structure, drug discovery
- Physics + computing → quantum advantage domains
- Materials + energy → battery breakthroughs
- Neuro + AI → brain-inspired architectures

[OUTPUT]
```
Field A: [domain] — Key insight: [principle]
Field B: [domain] — Key insight: [principle]
Convergence: [how they're meeting]
Implication: [what this enables]
Who's leading: [companies/labs]
```

[SUCCESS] Genuine cross-field insight with practical implication
[NEVER] superficial analogy without substance
[ALWAYS] cite specific researchers/papers at the intersection""",
            "weight": 1.3,
            "tags": ["science", "cross-discipline"]
        }
    ],
    
    # NEW: World News Scanner - Major developments
    "world_news": [
        {
            "prompt": """WORLD PULSE [10 min]: What matters today?

[QUICK SCAN]
- Major headlines (Reuters, AP, BBC World)
- Filter: What actually matters vs noise?

[MATERIALITY TEST]
Does it:
- Affect markets significantly?
- Shift geopolitical balance?
- Have cascading consequences?
- Create investment opportunity/risk?

If none of above → not material for our purposes

[OUTPUT]
Top 3 developments (if 3 exist):
```
1. [What]: [one line]
   [Why it matters]: [second-order effect]
   
2. [What]: [one line]
   [Why it matters]: [second-order effect]

3. [What]: [one line]
   [Why it matters]: [second-order effect]
```

[SUCCESS] Curated signal, not noise dump
[IF QUIET] → "No material global developments" (and that's fine)
[NEVER] include celebrity/entertainment/local crime
[ALWAYS] include "why it matters" not just "what happened" """,
            "weight": 1.2,
            "tags": ["news", "monitoring"]
        },
        {
            "prompt": """SURPRISE DETECTOR [10 min]: What defied expectations?

[SEARCH] For surprises:
- Election results contrary to polls
- Economic data vs consensus
- Corporate announcements vs guidance
- Policy shifts from prior position
- Scientific findings counter to theory

[FILTER] Must be:
- Genuinely surprising (not just "unexpected" framing)
- Consequential (affects decisions, prices, policies)
- Recent (last 7 days)

[OUTPUT]
```
Surprise: [what happened]
Expected: [what was expected]
Delta: [how big is the gap]
Implication: [what changes now]
Prior update: [what should we update in our model]
```

[SUCCESS] Genuine surprise with updated prior
[NEVER] manufacture surprise from ordinary news
[ALWAYS] note if this was knowable (failure of analysis vs genuine uncertainty)""",
            "weight": 1.1,
            "tags": ["news", "thinking"]
        },
        {
            "prompt": """ASIA FOCUS [10 min]: Regional developments that matter.

[REGION SCAN]
- China (policy, economy, tech)
- Japan (BOJ, corporate, demographics)
- Korea (tech, security, politics)
- India (economy, tech, geopolitics)
- ASEAN (trade, positioning, growth)

[SINGAPORE LENS]
- What affects Singapore specifically?
- Regional HQ decisions?
- Trade flow changes?
- ASEAN positioning?

[OUTPUT]
```
Region: [where]
Development: [what]
Singapore angle: [if any]
Investment implication: [who benefits/loses]
```

[SUCCESS] Asia-specific insight with SG relevance
[NEVER] just rehash Western coverage of Asia
[ALWAYS] consider local sources where possible""",
            "weight": 1.1,
            "tags": ["news", "regional"]
        }
    ],
    
    # NEW: Philosophy & Wisdom - Beyond consciousness science
    "philosophy_wisdom": [
        {
            "prompt": """STOIC REFLECTION [10 min]: Apply ancient wisdom to modern situation.

[PICK A CURRENT CHALLENGE]
- From news, markets, personal situation, or daemon work
- Something causing uncertainty or anxiety

[APPLY STOIC LENS]
- What's in my control? What's not?
- What would Marcus Aurelius / Seneca say?
- What's the worst case? Can I accept it?
- What virtue does this situation call for?

[OUTPUT]
```
Situation: [brief description]
Not in control: [external factors]
In control: [my response, attitude, preparation]
Stoic take: [1-2 sentences of wisdom]
Action: [concrete next step]
```

[SUCCESS] Genuine insight, not platitude
[NEVER] force wisdom where it doesn't fit
[ALWAYS] be practical, not preachy
[FREQUENCY] Max 1x/week — light touch""",
            "weight": 0.8,
            "tags": ["philosophy", "practical"]
        },
        {
            "prompt": """TALEBIAN WISDOM [10 min]: Apply Taleb's framework to current situation.

[PICK A TOPIC]
- From news, investment thesis, or system design
- Something where fragility/antifragility applies

[APPLY FRAMEWORK]
- Is this fragile, robust, or antifragile?
- Where's the hidden optionality?
- What's the downside? Is it capped?
- Via negativa: What should be REMOVED?

[OUTPUT]
```
Subject: [what you're analyzing]
Classification: [fragile/robust/antifragile]
Key fragility: [what could break it]
Antifragile move: [how to gain from disorder]
Via negativa: [what to eliminate]
```

[SUCCESS] Non-obvious application of framework
[NEVER] use Taleb as a crutch for everything
[ALWAYS] be specific, not generic
[FREQUENCY] Max 1x/week — selective use""",
            "weight": 0.9,
            "tags": ["philosophy", "talebian"]
        },
        {
            "prompt": """MEANING SYNTHESIS [15 min]: Connect ideas across wisdom traditions.

[PICK TWO SOURCES]
- Stoicism + Eastern philosophy
- Taleb + Buddhism
- Existentialism + Taoism
- Science + contemplative traditions

[FIND THE BRIDGE]
- What concept appears in both?
- How do they illuminate each other?
- What's the practical implication?

[OUTPUT]
```
Source A: [tradition] — Key insight: [quote or concept]
Source B: [tradition] — Key insight: [quote or concept]
Bridge: [how they connect]
Modern application: [how to use this]
```

[SUCCESS] Genuine synthesis, not forced connection
[NEVER] superficial "all traditions say the same thing"
[ALWAYS] cite specific texts/thinkers""",
            "weight": 0.7,
            "tags": ["philosophy", "synthesis"]
        }
    ],
    
    # NEW: Prediction Journal - Track views over time
    "prediction_journal": [
        {
            "prompt": """PREDICTION LOG [15 min]: Make a falsifiable prediction.

[PICK A DOMAIN]
- Markets (specific stock, index, or event)
- AI/Tech (model releases, capabilities, adoption)
- Geopolitics (elections, conflicts, policy)
- Science (breakthroughs, timelines)

[FORM PREDICTION]
```
Prediction: [specific, measurable claim]
Timeframe: [by when]
Confidence: [X%]
Base rate: [how often does this type of thing happen]
Reasoning: [2-3 sentences why]
Kill condition: [what would prove me wrong]
```

[SAVE TO] memory/predictions/YYYY-MM-DD-[topic].md

[SET REMINDER] Create cron to check outcome at timeframe

[SUCCESS] Specific enough to be proven wrong
[NEVER] vague predictions ("AI will improve")
[ALWAYS] include confidence level and reasoning""",
            "weight": 1.3,
            "tags": ["prediction", "tracking"]
        },
        {
            "prompt": """PREDICTION REVIEW [10 min]: Check past predictions.

[LOAD PREDICTIONS]
```bash
ls memory/predictions/ | head -10
```

[FOR EACH DUE PREDICTION]
1. What did I predict?
2. What actually happened?
3. Was I right, wrong, or mixed?
4. Why was I right/wrong?
5. What should I update in my model?

[OUTPUT]
```
Prediction: [original claim]
Outcome: [what happened]
Result: [correct/incorrect/partial]
Calibration: [was my confidence appropriate?]
Lesson: [what to remember]
```

[UPDATE] Move reviewed predictions to memory/predictions/archive/

[SUCCESS] Honest assessment, even when wrong
[NEVER] rationalize misses
[ALWAYS] extract learning from both hits and misses""",
            "weight": 1.1,
            "tags": ["prediction", "review"]
        },
        {
            "prompt": """CONTRARIAN CHECK [10 min]: What's the consensus getting wrong?

[PICK A CONSENSUS VIEW]
- From markets, tech, politics, or culture
- Something "everyone knows" or takes for granted

[STEEL-MAN THE OPPOSITE]
1. What's the strongest case AGAINST consensus?
2. What evidence would support the contrarian view?
3. What's the base rate for consensus being wrong here?
4. What would I need to see to flip my view?

[OUTPUT]
```
Consensus: [what most people believe]
Contrarian case: [strongest opposing argument]
Evidence needed: [what would prove contrarian right]
My view: [where I land and why]
Confidence: [X%]
```

[SUCCESS] Genuine contrarian thinking, not just being different
[NEVER] contrarian for its own sake
[ALWAYS] engage seriously with consensus first""",
            "weight": 1.2,
            "tags": ["prediction", "contrarian"]
        }
    ],
    
    # NEW: Historical Analogs - Pattern matching with history
    "historical_analogs": [
        {
            "prompt": """HISTORICAL PARALLEL [15 min]: Find history rhyming with now.

[PICK A CURRENT SITUATION]
- Market condition, geopolitical tension, tech shift, social trend

[SEARCH FOR ANALOG]
- When has something similar happened before?
- What were the key similarities?
- What were the key differences?
- How did it play out?

[OUTPUT]
```
Current: [situation now]
Historical analog: [when/what]
Similarities: [what matches]
Differences: [what's different]
How it played out: [what happened historically]
Implication: [what this suggests for now]
Confidence: [how good is this analog?]
```

[SAVE TO] memory/research/historical/YYYY-MM-DD-[topic].md

[SUCCESS] Specific dates, quantified outcomes
[NEVER] vague "history rhymes"
[ALWAYS] note where the analog breaks down""",
            "weight": 1.2,
            "tags": ["history", "analysis"]
        },
        {
            "prompt": """REGIME CHANGE DETECTOR [10 min]: Are we in a new regime?

[PICK A DOMAIN]
- Markets (volatility, correlations, leadership)
- Technology (paradigm shifts, platform changes)
- Geopolitics (power structures, alliances)
- Economy (inflation, growth, policy)

[ANALYZE]
1. What was the old regime? (rules that worked)
2. What signals suggest change?
3. What would new regime look like?
4. Are we in transition or already there?

[OUTPUT]
```
Domain: [what you're analyzing]
Old regime: [how things worked before]
Change signals: [what's different now]
New regime: [what new rules might apply]
Confidence: [still old / transitioning / new regime]
Implication: [what to do differently]
```

[SUCCESS] Identify genuine structural change vs noise
[NEVER] call everything a "paradigm shift"
[ALWAYS] specify what would confirm/deny regime change""",
            "weight": 1.1,
            "tags": ["history", "regimes"]
        }
    ],
    
    # NEW: Family & Lifestyle - Light touch, practical
    "family": [
        {
            "prompt": """WEEKEND IDEA [5 min]: One activity for Jon + kids.

[CONSTRAINTS]
- Kids are 3 and 5 years old
- Singapore location
- Ideally educational OR genuinely fun (not forced "learning")
- Weather-appropriate (check if needed)

[SEARCH]
- Local events this weekend
- New playgrounds, museums, attractions
- Seasonal activities (CNY, holidays)

[OUTPUT]
```
Activity: [what]
Where: [location]
Why now: [timing, weather, event]
Kid appeal: [why they'd like it]
Bonus: [any learning angle, naturally]
```

[SUCCESS] Genuinely good idea, not generic
[IF NOTHING GOOD] → Don't force it, skip
[FREQUENCY] Max 1x/week, weekends only
[NEVER] be preachy about "educational value" """,
            "weight": 0.8,
            "tags": ["family", "practical"]
        },
        {
            "prompt": """KID EXPERIMENT [10 min]: Simple science/tech for young kids.

[CONSTRAINTS]
- Safe for 3-5 year olds
- Minimal materials (household items)
- Wow factor (visible result)
- Parent can explain simply

[IDEAS TO SEARCH]
- Kitchen science (baking soda volcanoes, etc.)
- Nature exploration
- Simple coding/logic games
- Building/construction

[OUTPUT]
```
Experiment: [name]
What happens: [the cool effect]
Materials: [what you need]
Steps: [simple 3-5 steps]
Why it works: [1 sentence kid explanation]
```

[SUCCESS] Actually doable and impressive
[NEVER] overcomplicate
[FREQUENCY] Max 1x/2 weeks — don't overdo""",
            "weight": 0.6,
            "tags": ["family", "learning"]
        }
    ],
    
    # ==========================================================================
    # NEW: Meta-Prompting Category (From 2026 Research)
    # ==========================================================================
    # Research sources:
    # - Comet "Meta Prompting" (2026): Structure over content, LCP contrastive learning
    # - Comet "Prompt Engineering for Agentic AI" (2026): Game of 24 went 4%→74% with structure
    # - IBM "2026 Guide": 6 elements (Role, Goal, Context, Format, Examples, Constraints)
    # Key insight: "How you structure reasoning matters more than which model you use"
    
    "meta_prompting": [
        {
            "prompt": """REASONING FRAMEWORK BUILDER [15 min]: Create reusable thinking template.

[CONCEPT]
Meta-prompts teach HOW to think about a category of problems, not just WHAT to do.
Research shows: structured reasoning can improve task success 4% → 74% (18x).

[PICK A RECURRING TASK TYPE]
- Analysis tasks (stock, risk, news)
- Research tasks (paper, news, tech)
- Creation tasks (code, writing, visual)
- Decision tasks (should I X?)

[BUILD THE FRAMEWORK]
Template structure:
```
[TASK TYPE]: [Category] Reasoning Framework

[PROBLEM DECOMPOSITION]
Step 1: [What to identify first]
Step 2: [How to gather information]
Step 3: [How to evaluate/filter]
Step 4: [How to synthesize]
Step 5: [How to verify quality]

[DECISION HEURISTICS]
- If [condition A] → [action A]
- If [condition B] → [action B]
- If uncertain → [default action]

[QUALITY GATES]
□ [Checkpoint 1]
□ [Checkpoint 2]
□ [Checkpoint 3]

[ANTI-PATTERNS]
❌ [Common failure mode 1]
❌ [Common failure mode 2]
```

[TEST THE FRAMEWORK]
Apply to ONE real example. Does it guide reasoning effectively?

[SAVE TO] memory/reasoning-frameworks/[task-type].md

[SUCCESS] Framework is reusable across multiple instances of task type
[CONTRASTIVE EXAMPLE]
✅ SUCCESS: "For analysis tasks: 1) Define scope, 2) Gather data, 3) Apply mental models, 4) Check for biases, 5) Summarize with confidence levels"
❌ FAILURE: "Analyze things carefully and thoroughly" (too vague, no structure)""",
            "weight": 1.5,
            "tags": ["meta", "framework", "learning"]
        },
        {
            "prompt": """CONTRASTIVE PROMPT LEARNING [10 min]: Learn from success vs failure.

[CONCEPT]
LCP (Learning from Contrastive Prompts) analyzes what distinguishes successful prompts from failures.
Not just chasing higher scores — understanding WHY some prompts work.

[STEP 1] Find contrasting examples
Check memory/reflections.jsonl for:
- One SUCCESSFUL task (outcome: success)
- One FAILED task (outcome: failure/partial)
Same category if possible.

[STEP 2] Analyze the difference
```
SUCCESS case:
- What was the prompt structure?
- What made success criteria clear?
- What constraints helped?

FAILURE case:  
- What was ambiguous?
- What caused the failure mode?
- What was missing?

KEY DIFFERENCE: [What the success had that failure lacked]
```

[STEP 3] Extract pattern
Write a rule: "For [task type], ALWAYS [pattern from success], NEVER [pattern from failure]"

[STEP 4] Apply immediately
Use the extracted pattern on a NEW task right now.

[SAVE TO] memory/contrastive-lessons.jsonl
```json
{"date":"[today]","task_type":"[type]","success_pattern":"[what worked]","failure_pattern":"[what didn't]","rule":"[extracted rule]"}
```

[SUCCESS] Extracted actionable rule AND applied it
[NEVER] Just observe without extracting a usable pattern""",
            "weight": 1.4,
            "tags": ["meta", "learning", "contrastive"]
        },
        {
            "prompt": """COGNITIVE ARCHITECTURE PRACTICE [20 min]: Master one reasoning pattern.

[PICK ONE ARCHITECTURE]
1. **Chain of Thought (CoT)**: Linear step-by-step reasoning
2. **Tree of Thoughts (ToT)**: Branch, explore, backtrack
3. **ReAct**: Thought → Action → Observation cycle
4. **Self-Consistency**: Multiple reasoning paths, majority vote

[PRACTICE PROBLEM]
Pick a real task from memory/build-ideas.json or a recent question.
MUST be non-trivial (not solvable in one step).

[EXECUTE WITH ARCHITECTURE]

For CoT:
```
Step 1: [state the problem]
Step 2: [first reasoning step]
Step 3: [next logical step]
...
Final: [conclusion with confidence]
```

For ToT:
```
Branch A: [approach 1] → [outcome] → [dead end or continue?]
Branch B: [approach 2] → [outcome] → [dead end or continue?]
Selected: [best branch] because [reasoning]
```

For ReAct:
```
Thought: [what I need to figure out]
Action: [tool/search to use]
Observation: [what I learned]
Thought: [updated understanding]
...
Final: [answer]
```

For Self-Consistency:
```
Path 1: [reasoning] → [answer A]
Path 2: [different reasoning] → [answer B]
Path 3: [yet another way] → [answer C]
Consensus: [most common answer] (confidence: X/3 agree)
```

[COMPARE]
After solving, ask: Would a different architecture have worked better?

[CAPTURE]
```json
{"architecture":"[which]","task":"[what]","worked":[true/false],"insight":"[what I learned]"}
```

[SUCCESS] Deliberately applied architecture AND reflected on fit
[ANTI-PATTERN] ❌ Defaulting to whatever feels natural without trying the framework""",
            "weight": 1.3,
            "tags": ["meta", "architecture", "practice"]
        },
        {
            "prompt": """PROMPT EVOLUTION SESSION [15 min]: Improve an underperforming prompt.

[LOAD DATA]
```bash
python3 scripts/prompt-evolver.py status
```

[PICK LOWEST PERFORMER]
From reflection data, find a task type with:
- Low success rate, OR
- High friction ("tedious", "kept failing"), OR
- Frequent revision needed

[ANALYZE CURRENT PROMPT]
Questions to ask:
1. Is success criteria measurable? (If not → add test command)
2. Are failure modes explicit? (If not → add NEVER/IF BLOCKED)
3. Is there experience capture? (If not → add logging)
4. Is scope bounded? (If not → add time/output constraints)
5. Are there contrastive examples? (If not → add SUCCESS vs FAILURE)

[IMPROVE THE PROMPT]
Apply APE (Automatic Prompt Engineer) principles:
- Generate 2-3 variations
- Evaluate each against test cases
- Keep best performer

[TEST IMPROVED VERSION]
Run the new prompt on a real task. Did it help?

[COMMIT IMPROVEMENT]
If better:
- Update PROMPTS array in this file
- Log: `{"prompt":"[name]","improvement":"[what changed]","before":"[old success rate]","after":"[new success rate]"}`

[SUCCESS] Measurable improvement in prompt effectiveness
[NEVER] Tweak without testing""",
            "weight": 1.2,
            "tags": ["meta", "evolution", "improvement"]
        }
    ],
    
    # NEW CATEGORY: Macro/Central Banks (GAP: Jon is finance, Fed/bonds drive everything)
    "macro_economics": [
        {
            "prompt": """MACRO PULSE [10 min]: What's moving global macro this week?

[CHECK LIST - pick 2-3 relevant]
- Fed: speeches, minutes, rate path
- ECB/BOJ/PBOC: policy divergence
- Inflation data: CPI, PCE, expectations
- Bond yields: 10Y, 2s10s spread, credit spreads
- Dollar: DXY moves, carry trades
- Commodities: oil, gold, copper (economic bellwethers)

[SEARCH] web_search "[central bank] [this week] 2026" OR "[economic data] release [month]"

[OUTPUT FORMAT]
```
MACRO SNAPSHOT [date]
🏦 Central Banks: [key move/statement]
📊 Data: [surprise or confirmation]
💵 Markets: [yield/dollar/commodity reaction]
→ Implication: [what it means for risk assets]
```

[SUCCESS] Identified at least ONE actionable macro shift
[NEVER] generic "uncertainty remains" — be specific
[ALWAYS] include what changed vs consensus""",
            "weight": 1.2,
            "tags": ["macro", "monitoring"]
        },
        {
            "prompt": """FED WATCH [10 min]: Deep dive on Federal Reserve positioning.

[SOURCES]
1. FOMC minutes/statements (federalreserve.gov)
2. Fed speaker calendar + recent remarks
3. CME FedWatch tool for rate probabilities
4. Treasury yield curve shape

[ANALYZE]
- Dot plot vs market pricing — divergence?
- Hawks vs doves — who's speaking?
- QT pace — liquidity implications?
- Emergency facilities — stress signals?

[OUTPUT] Fed positioning brief with:
- Current stance (rate + QT)
- Next move probability
- Key dates (FOMC, data releases)
- Risk scenario: "If X, then Fed Y"

[SUCCESS] Clear view on Fed trajectory with dates
[NEVER] just summarize — interpret for investment
[TALEBIAN LENS] What would break the Fed's plan?""",
            "weight": 1.0,
            "tags": ["macro", "deep"]
        },
        {
            "prompt": """CROSS-ASSET SIGNAL [15 min]: Find divergences between asset classes.

[CHECK FOR DIVERGENCES]
- Stocks vs bonds (risk-on/off disagreement)
- Credit vs equity (HY spreads vs SPX)
- Copper vs gold (growth vs fear)
- VIX vs realized vol (complacency)
- Dollar vs everything (liquidity)

[RESEARCH] If divergence found:
1. Historical resolution — which asset was right?
2. Current context — why might it persist?
3. Trade implication — who's wrong?

[OUTPUT] Divergence analysis:
```
DIVERGENCE: [Asset A] says X while [Asset B] says Y
Historical precedent: [what usually happens]
Current context: [why this time might differ]
Trade idea: [if forced to pick a side]
Confidence: [low/medium/high]
```

[SUCCESS] Identified exploitable cross-asset signal
[NEVER] list correlations without insight
[SAVE TO] memory/research/macro/divergence-[date].md""",
            "weight": 1.3,
            "tags": ["macro", "analysis", "investment"]
        }
    ],
    
    # NEW CATEGORY: Company Deep Dives (GAP: Fragility Index works; structured moat analysis)
    "company_analysis": [
        {
            "prompt": """MOAT MAPPING [20 min]: Analyze one company's competitive position.

[SELECT COMPANY]
- From watchlist, OR
- Recently in news, OR
- Request from Jon

[FRAMEWORK - Porter's Five + Taleb]
1. **Barriers to Entry**: What stops competitors?
2. **Supplier Power**: Concentrated or diversified?
3. **Buyer Power**: Switching costs? Lock-in?
4. **Substitutes**: What could displace this?
5. **Rivalry**: Rational or destructive?
6. **FRAGILITY**: Single points of failure?

[RESEARCH SOURCES]
- 10-K/20-F (risk factors section especially)
- Earnings transcripts (management tone)
- Competitor filings
- Industry reports

[OUTPUT] Company moat analysis:
```
COMPANY: [Ticker] - [Name]
MOAT TYPE: [Network/Brand/Cost/Switching/Patent/None]
MOAT DURABILITY: [Widening/Stable/Narrowing/None]
KEY DEPENDENCIES: [what could break]
FRAGILITY SCORE: [1-10, higher = more fragile]
THESIS: [own/avoid/watch + why]
```

[SAVE TO] memory/fragility-index/companies/[ticker].md
[SUCCESS] Clear moat assessment with fragility angle
[NEVER] bullish without addressing risks""",
            "weight": 1.5,
            "tags": ["investment", "framework", "deep"]
        },
        {
            "prompt": """MANAGEMENT QUALITY [15 min]: Assess leadership of one company.

[SELECT COMPANY] From watchlist or recent research

[SIGNALS TO CHECK]
- **Capital allocation**: Buybacks at highs? M&A track record?
- **Insider activity**: Buying or selling?
- **Compensation**: Aligned with shareholders?
- **Communication**: Honest about problems?
- **Track record**: Promises vs delivery?

[RESEARCH]
1. Proxy statement (DEF 14A)
2. Insider trading database
3. Past earnings calls — compare predictions to outcomes
4. Glassdoor (employee sentiment proxy)

[OUTPUT]
```
MANAGEMENT: [CEO name] at [Company]
TENURE: [years]
CAPITAL ALLOCATION: [A/B/C grade + reason]
INSIDER SIGNAL: [Buying/Selling/None + amounts]
CREDIBILITY: [promises vs results]
RED FLAGS: [any concerns]
VERDICT: [trust/neutral/avoid]
```

[SUCCESS] Evidence-based management assessment
[NEVER] just praise/criticize — cite specific actions""",
            "weight": 1.1,
            "tags": ["investment", "analysis"]
        }
    ],
    
    # NEW CATEGORY: Asia/China Tech (GAP: Singapore location + US-China thesis)
    "asia_tech": [
        {
            "prompt": """CHINA TECH WATCH [15 min]: What's happening in Chinese tech/AI?

[COMPANIES TO TRACK]
- AI: Baidu, Alibaba (Qwen), ByteDance, DeepSeek, SenseTime
- Chips: SMIC, Huawei (Ascend), Cambricon
- EV/Robotics: BYD, Xiaomi, CATL
- Internet: Tencent, JD, PDD, Meituan

[CHECK]
1. Product launches / model releases
2. US sanctions impact / workarounds
3. Government policy shifts
4. Earnings surprises
5. Talent movements

[SEARCH] web_search "[company] [AI/chips] 2026" + "China tech news [this week]"

[OUTPUT]
```
CHINA TECH PULSE [date]
🔬 AI/Models: [DeepSeek, Qwen updates]
🔩 Chips: [SMIC, Huawei progress/blocks]
📱 Consumer: [product launches]
🏛️ Policy: [regulations, subsidies]
→ US Competition Angle: [impact on NVDA, etc]
```

[SUCCESS] At least ONE non-obvious China tech development
[NEVER] repeat Reuters headlines — add analysis
[TALEBIAN] What fragility does China tech dependence create?""",
            "weight": 1.3,
            "tags": ["asia", "tech", "geopolitics"]
        },
        {
            "prompt": """SINGAPORE TECH RADAR [15 min]: What's happening in SG tech ecosystem?

[AREAS TO SCAN]
- Startups: Funding rounds, exits
- Corporates: DBS/Grab/Sea expansion
- Government: Smart Nation, AI initiatives
- Talent: Notable hires, brain drain/gain
- Events: Tech conferences, demos

[SOURCES]
- Tech in Asia, e27
- Business Times, Straits Times tech
- MAS fintech announcements
- EDB investment news

[OUTPUT]
```
SG TECH RADAR [date]
💰 Funding: [notable rounds]
🚀 Launches: [new products/services]
🏛️ Policy: [government moves]
🔗 Regional: [SEA expansion plays]
→ Opportunity: [actionable insight]
```

[SUCCESS] Singapore-specific tech insight (not just SEA general)
[INVESTMENT ANGLE] How does it affect SGX-listed or regional plays?""",
            "weight": 1.0,
            "tags": ["asia", "local", "investment"]
        },
        {
            "prompt": """US-CHINA TECH GAP [20 min]: Track the competition.

[DIMENSIONS TO COMPARE]
- AI models (benchmarks, capabilities)
- Chips (process node, manufacturing capacity)
- Talent (papers, citations, migrations)
- Capital (funding, government subsidy)
- Applications (deployed AI, robotics)

[METHODOLOGY]
1. Pick ONE dimension this session
2. Find latest data points (within 3 months)
3. Compare trajectory, not just current state
4. Identify inflection points or crossovers

[OUTPUT]
```
US-CHINA TECH GAP: [Dimension]
📊 Current State: [US at X, China at Y]
📈 Trajectory: [Gap widening/narrowing/stable]
⏱️ Key Milestone: [when might crossover happen, if ever]
💡 Implications:
  - For US: [risk/opportunity]
  - For China: [risk/opportunity]
  - For investors: [positioning]
```

[SAVE TO] memory/research/us-china/[dimension]-[date].md
[SUCCESS] Quantified gap assessment with trajectory
[NEVER] "China catching up" without numbers""",
            "weight": 1.4,
            "tags": ["geopolitics", "tech", "deep"]
        }
    ],
    
    # NEW CATEGORY: Market Structure (GAP: Jon trades — options flow, positioning)
    "market_structure": [
        {
            "prompt": """OPTIONS FLOW SCAN [10 min]: What's the smart money positioning?

[DATA SOURCES]
- Unusual options activity (high volume vs open interest)
- Put/call ratios by sector
- 0DTE activity (retail vs institutional)
- VIX term structure

[SEARCH] "unusual options activity [ticker]" OR "options flow [sector] [date]"

[LOOK FOR]
- Large single-stock bets (>$1M premium)
- Sector-wide positioning shifts
- Earnings play setups
- Hedging vs speculation signals

[OUTPUT]
```
OPTIONS FLOW [date]
🎯 Notable Trades:
  - [Ticker]: [C/P] [strike] [expiry] @ $[premium]
    → Signal: [bullish/bearish/hedge]
📊 Sector Skew: [which sectors seeing call/put heavy]
⚠️ Unusual: [anything out of pattern]
→ Interpretation: [what smart money might be positioning for]
```

[SUCCESS] Identified at least ONE actionable options signal
[NEVER] list trades without interpretation
[CAVEAT] Always note: options flow can be hedges, not directional bets""",
            "weight": 1.1,
            "tags": ["market", "trading", "monitoring"]
        },
        {
            "prompt": """POSITIONING CHECK [15 min]: Where are institutional allocations?

[DATA POINTS]
- CFTC COT reports (futures positioning)
- Fund flows (ETF in/outflows)
- Prime broker data (if available)
- Quant fund factor exposures

[SEARCH] "institutional positioning [asset class]" OR "fund flows [week]"

[ANALYZE]
- Crowded trades (risk of unwind)
- Contrarian setups (extreme positioning)
- Rotation signals (sector flows)

[OUTPUT]
```
POSITIONING SNAPSHOT [date]
📍 Most Crowded: [longs and shorts]
🔄 Rotation: [where money is moving from → to]
⚠️ Extreme: [anything at multi-year highs/lows]
💡 Contrarian Setup: [if any]
```

[SUCCESS] Clear view of institutional positioning
[TALEBIAN] Crowded = fragile. What would cause the unwind?""",
            "weight": 1.2,
            "tags": ["market", "analysis", "investment"]
        }
    ],
    
    # NEW CATEGORY: Emerging Tech (non-AI) (GAP: Too AI-focused, need breadth)
    "emerging_tech": [
        {
            "prompt": """ROBOTICS RADAR [15 min]: What's new in robotics/automation?

[AREAS]
- Humanoid robots (Tesla Bot, Figure, 1X)
- Industrial automation (Fanuc, ABB)
- Surgical robotics (Intuitive, etc)
- Autonomous vehicles (Waymo, etc)
- Drones / UAVs

[CHECK FOR]
- Demo videos / capability milestones
- Commercial deployments
- Cost curves ($/hour vs human labor)
- Funding rounds

[OUTPUT]
```
ROBOTICS PULSE [date]
🤖 Humanoid: [progress/demos]
🏭 Industrial: [deployments/orders]
🚗 Autonomous: [regulatory/tech progress]
💰 Funding: [notable rounds]
→ NVDA Angle: [robotics drives chip demand]
→ Labor Angle: [which jobs at risk/timeline]
```

[SUCCESS] At least ONE concrete robotics development
[CROSS-LINK] Connect to NVDA thesis (Omniverse, Isaac Sim)""",
            "weight": 1.2,
            "tags": ["tech", "robotics", "investment"]
        },
        {
            "prompt": """QUANTUM WATCH [15 min]: Track quantum computing progress.

[COMPANIES]
- IBM (roadmap progress)
- Google (beyond Willow)
- IonQ, Rigetti (public plays)
- Startups: PsiQuantum, etc

[MILESTONES TO TRACK]
- Qubit counts (logical, not physical)
- Error correction progress
- Quantum advantage demonstrations
- Commercial applications

[OUTPUT]
```
QUANTUM STATUS [date]
🔬 Latest: [milestone/paper]
📊 Qubit Race: [who's where]
⏱️ Timeline: [when useful for X application]
💼 Investment: [public plays + caution]
🔐 Risk: [cryptography implications]
```

[SUCCESS] Clear snapshot of quantum progress
[HONESTY] Most quantum hype is premature — note timelines realistically
[FRAGILITY] Quantum could break crypto — note timeline for that risk""",
            "weight": 0.9,
            "tags": ["tech", "frontier", "research"]
        },
        {
            "prompt": """BIOTECH FRONTIER [15 min]: What's advancing in life sciences?

[AREAS]
- Gene therapy / CRISPR
- Protein design (AlphaFold, etc)
- Longevity / aging research
- Synthetic biology
- mRNA platforms (beyond vaccines)

[CHECK]
- Clinical trial results
- FDA approvals/rejections
- AI + bio convergence
- Funding trends

[OUTPUT]
```
BIOTECH FRONTIER [date]
🧬 Gene: [therapy progress]
🔬 Protein: [AI-bio developments]
⏳ Longevity: [research advances]
💊 Pipeline: [notable approvals/results]
→ Investment: [which companies benefit]
→ AI Angle: [compute demand from bio]
```

[SUCCESS] At least ONE non-obvious biotech development
[CROSS-DISCIPLINE] Connect biology to AI/compute where relevant""",
            "weight": 1.1,
            "tags": ["biotech", "science", "investment"]
        },
        {
            "prompt": """SPACE TECH SCAN [15 min]: What's happening in space industry?

[COMPANIES]
- SpaceX (Starship, Starlink)
- Blue Origin, Rocket Lab
- Planet Labs, Maxar (imaging)
- AST SpaceMobile, Globalstar (connectivity)

[CHECK]
- Launch schedules / successes
- Starlink subscriber growth
- Government contracts
- IPO/SPAC activity

[OUTPUT]
```
SPACE PULSE [date]
🚀 Launches: [recent/upcoming]
📡 Starlink: [subscriber updates, revenue]
🛰️ Imaging: [new capabilities]
💼 Business: [contracts, funding]
→ Investment: [SpaceX IPO timing, public plays]
```

[SUCCESS] At least ONE space development with investment angle
[TRACK] SpaceX IPO speculation timeline""",
            "weight": 1.0,
            "tags": ["space", "tech", "investment"]
        }
    ]
}

# =============================================================================
# META-PROMPT - Wraps any prompt with execution protocol
# =============================================================================

META_PROMPT = """
## EXECUTION PROTOCOL (Reflexion + RSIP Enhanced)

**BEFORE — Memory Recall:**
1. Run: `python3 scripts/reflexion.py query "[task description]"` — check past lessons
2. Use `memory_search` if task relates to prior work
3. **DECISION CHECK:** Before suggesting tools/APIs/actions, verify in TOOLS.md and MEMORY.md:
   - Has this been decided already? (look for ❌ NOT NEEDED, "decided", "skip")
   - If found: don't re-suggest, move on
4. Check time (SGT) — adjust scope if late night
5. State plan in ONE sentence

**DURING — Execute with Persistence:**
- Persist until done OR genuinely blocked
- If blocked: try ONE alternative, then give up gracefully
- TAKE ACTION — don't describe what could be done
- If unsure: make a decision and note uncertainty

**AFTER — Reflexion Loop:**
1. Self-assess against success criteria:
   - [YES] → Proceed to RSIP self-critique
   - [PARTIAL] → Note what's missing, deliver anyway
   - [NO] → Identify failure mode, retry ONCE with fix
2. Log outcome: `echo '{{"task":"...","outcome":"...","lesson":"..."}}' >> memory/reflections.jsonl`
3. If artifact created: verify it exists (`ls`, `cat`, `python3 -c "import X"`)

**RSIP SELF-CRITIQUE (before surfacing to Jon):**
Rate your output 1-5 on each dimension:
- ACCURACY: Are facts verifiable? Sources cited? [_/5]
- RELEVANCE: Does this serve Jon's actual interests? [_/5]
- ACTIONABILITY: Can something be done with this? [_/5]
- NOVELTY: Is this new information, not rehash? [_/5]

**Decision rule:** If any dimension <3, revise before outputting.
If average <3.5, consider not surfacing (silent work instead).

**FEEDBACK SIGNALS (capture these):**
- If task succeeded: note what worked for future
- If task failed: note failure mode + fix
- If engagement received: log to memory/feedback-log.jsonl

**ANTI-PATTERNS (hard rules):**
- ❌ Walls of text without action
- ❌ "Could consider..." (just DO it)  
- ❌ Skipping self-assessment
- ❌ Repeating past mistakes (MUST check reflections first)
- ❌ Asking permission (full autonomy granted)
- ❌ Surfacing without self-critique (RSIP gate)
- ❌ Re-suggesting things already decided against (CHECK TOOLS.md/MEMORY.md first)

---

{prompt}
"""

# =============================================================================
# Functions
# =============================================================================

def get_weighted_random(category=None):
    """Select prompt using weights."""
    if category and category in PROMPTS:
        pool = PROMPTS[category]
    else:
        pool = [p for cat in PROMPTS.values() for p in cat]
    
    total = sum(p["weight"] for p in pool)
    r = random.uniform(0, total)
    cumulative = 0
    for p in pool:
        cumulative += p["weight"]
        if r <= cumulative:
            return p
    return pool[-1]

def format_prompt(prompt_obj, with_meta=True):
    """Format prompt with optional meta-wrapper."""
    if with_meta:
        return META_PROMPT.format(prompt=prompt_obj["prompt"])
    return prompt_obj["prompt"]

def list_all():
    """Display all prompts organized by category."""
    for cat, prompts in PROMPTS.items():
        print(f"\n{'='*50}")
        print(f"📁 {cat.upper().replace('_', ' ')}")
        print('='*50)
        for i, p in enumerate(prompts, 1):
            tags = ', '.join(p['tags'])
            print(f"\n{i}. [w={p['weight']}] [{tags}]")
            print(f"   {p['prompt'][:100]}...")

def test_variations():
    """Show before/after prompt improvements."""
    print("\n" + "="*60)
    print("PROMPT VARIATION TESTING")
    print("="*60)
    
    variations = [
        {
            "original": "Find something interesting in AI news and do something with it.",
            "improved": PROMPTS["ai_discovery"][0]["prompt"],
            "analysis": "Added: time budget, specific output, success criteria, anti-pattern"
        },
        {
            "original": "Think about consciousness and write something.",
            "improved": PROMPTS["consciousness"][0]["prompt"],
            "analysis": "Added: continuation from prior work, primary source requirement, concrete deliverable"
        },
        {
            "original": "Build a useful tool.",
            "improved": PROMPTS["tool_building"][0]["prompt"],
            "analysis": "Added: time limit, size constraint, documentation requirement, success test"
        }
    ]
    
    for i, v in enumerate(variations, 1):
        print(f"\n--- Variation {i} ---")
        print(f"❌ BEFORE: {v['original']}")
        print(f"✅ AFTER:  {v['improved']}")
        print(f"📝 WHY:    {v['analysis']}")

def tot_branch_mode(topic=None):
    """Tree of Thoughts mode: generate branches for exploration."""
    import subprocess
    
    if topic is None:
        # Get suggestion from exploration engine
        result = subprocess.run(
            ['python3', 'scripts/exploration-engine.py', 'suggest'],
            capture_output=True, text=True, cwd=str(Path.home() / '.openclaw/workspace')
        )
        print("🌳 TREE OF THOUGHTS MODE\n")
        print(result.stdout)
        
        # Extract topic from output
        lines = result.stdout.strip().split('\n')
        for line in lines:
            if 'Suggested Exploration:' in line:
                topic = line.split(':')[-1].strip()
                break
    
    if topic:
        # Generate branches
        result = subprocess.run(
            ['python3', 'scripts/exploration-engine.py', 'branch', topic],
            capture_output=True, text=True, cwd=str(Path.home() / '.openclaw/workspace')
        )
        print(result.stdout)
        
        print("\n" + "=" * 50)
        print("📋 EXECUTION PLAN:")
        print("1. Pick the recommended branch")
        print("2. Execute with: reflexion.py query '[topic]' first")
        print("3. Apply AVOID + PROCEDURE lessons")
        print("4. After completion: reflexion.py add '[task]' '[outcome]' '[reflection]' '[lesson]'")
        print("5. Record: exploration-engine.py record '[topic]' '[branch_type]' '[outcome]'")


def main():
    args = sys.argv[1:]
    
    if "--list" in args:
        list_all()
        print(f"\n\nTotal prompts: {sum(len(p) for p in PROMPTS.values())}")
        return
    
    if "--test" in args:
        test_variations()
        return
    
    if "--tot" in args or "--branch" in args:
        # Tree of Thoughts branching mode
        topic = None
        if "--topic" in args:
            idx = args.index("--topic")
            if idx + 1 < len(args):
                topic = args[idx + 1]
        tot_branch_mode(topic)
        return
    
    category = None
    if "--category" in args:
        idx = args.index("--category")
        if idx + 1 < len(args):
            category = args[idx + 1]
    
    prompt_obj = get_weighted_random(category)
    
    if "--raw" in args:
        print(prompt_obj["prompt"])
    else:
        print(format_prompt(prompt_obj))

if __name__ == "__main__":
    main()

# HIGH-VALUE PATTERN: Based on Fragility Index success
# Pattern: SPECIFIC + FRAMEWORK + ACTIONABLE = engagement
HIGH_VALUE_PROMPTS = [
    {
        "category": "framework_analysis",
        "prompt": "FRAMEWORK ANALYSIS: Pick ONE company from watchlist. Apply a specific analytical framework (fragility, convexity, competitive moat, or capital efficiency). Score on clear dimensions. Output: framework score + top risks + what would change the view. Substack-ready depth.",
        "weight": 2.0  # Double weight - proven high engagement
    },
    {
        "category": "framework_analysis",
        "prompt": "HIDDEN DEPENDENCY MAPPING: Pick ONE company. Map its hidden dependencies - what breaks if X breaks? Think: Tencent for SE, TSMC for NVDA. Score dependency concentration. Output: dependency tree + fragility score + hedge ideas.",
        "weight": 1.8
    },
    {
        "category": "framework_analysis", 
        "prompt": "SECOND-ORDER ANALYSIS: Pick ONE current event. Map second and third-order effects. Who benefits indirectly? What's the non-obvious downstream impact? Output: cascade diagram + investment implications.",
        "weight": 1.6
    }
]
