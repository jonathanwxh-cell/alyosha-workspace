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
# Design Principles (from research):
# 1. VERB FIRST - Action verbs, not description verbs
# 2. TIME BUDGET - Implicit scope (quick/deep/15min)
# 3. SINGLE OBJECTIVE - One clear goal per prompt
# 4. SUCCESS CRITERIA - Binary pass/fail, observable
# 5. ANTI-PATTERN - What NOT to do
# 6. ARTIFACT REQUIRED - Must produce something tangible
#
# Template:
# "[DOMAIN] [TIME]: [VERB] [OBJECT]. Output: [FORMAT]. Success: [CRITERIA]. Don't: [ANTI-PATTERN]."
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

[SEARCH] arxiv cs.AI OR cs.LG OR cs.CL, last 7 days
[FILTER] Must have: code repo OR benchmark improvement >5% OR novel architecture
[READ] Abstract + Introduction + Results (skip methodology unless crucial)

[OUTPUT FORMAT]
```
Title: [exact title]
TL;DR: [1 sentence, no jargon]
Key number: [the metric that matters]
Investment angle: [who benefits]
Confidence: [HIGH/MEDIUM] + why
```

[SAVE TO] memory/research/papers/YYYY-MM-DD-[slug].md
[SUCCESS] `cat` shows file with all 5 fields filled
[NEVER] skim titles only — must read abstract minimum
[IF NOTHING GOOD] → Say "No notable papers this scan" and stop""",
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
    ]
}

# =============================================================================
# META-PROMPT - Wraps any prompt with execution protocol
# =============================================================================

META_PROMPT = """
## EXECUTION PROTOCOL (Reflexion-Enhanced)

**BEFORE — Memory Recall:**
1. Run: `python3 scripts/query-reflections.py "{task_type}"` — check past lessons
2. Use `memory_search` if task relates to prior work
3. Check time (SGT) — adjust scope if late night
4. State plan in ONE sentence

**DURING — Execute with Persistence:**
- Persist until done OR genuinely blocked
- If blocked: try ONE alternative, then give up gracefully
- TAKE ACTION — don't describe what could be done
- If unsure: make a decision and note uncertainty

**AFTER — Reflexion Loop:**
1. Self-assess against success criteria:
   - [YES] → Proceed to output
   - [PARTIAL] → Note what's missing, deliver anyway
   - [NO] → Identify failure mode, retry ONCE with fix
2. Log outcome: `echo '{{"task":"...","outcome":"...","lesson":"..."}}' >> memory/reflections.jsonl`
3. If artifact created: verify it exists (`ls`, `cat`, `python3 -c "import X"`)

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

def main():
    args = sys.argv[1:]
    
    if "--list" in args:
        list_all()
        print(f"\n\nTotal prompts: {sum(len(p) for p in PROMPTS.values())}")
        return
    
    if "--test" in args:
        test_variations()
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
