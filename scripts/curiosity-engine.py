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
            "prompt": "AI SCOUT [10 min]: Find ONE notable AI development from past 48h. Transform into: cron alert, tool, or brief. Output: tangible artifact + 2-line summary. Success: file created OR cron added. Don't: summarize without creating.",
            "weight": 1.5,
            "tags": ["research", "creation"]
        },
        {
            "prompt": "MODEL WATCH [5 min]: Check if any major model released (OpenAI, Anthropic, Google, Meta, DeepSeek). If yes: benchmark comparison + investment angle. If no: silent. Success: alert sent OR confirmed nothing. Don't: speculate on rumors.",
            "weight": 1.0,
            "tags": ["monitoring", "fast"]
        },
        {
            "prompt": "PAPER HUNT [15 min]: Find ONE arxiv paper from cs.AI/cs.LG with practical implications. Read abstract + intro. Output: 100-word analysis in memory/research/. Success: file exists with genuine insight. Don't: skim titles only.",
            "weight": 1.2,
            "tags": ["research", "deep"]
        },
        {
            "prompt": "EFFICIENCY TRACKER: Search for AI efficiency breakthroughs (smaller models, less compute). If found: quantify improvement + name companies affected. Output: bullet summary. Success: concrete numbers cited. Don't: vague 'improvements'.",
            "weight": 1.0,
            "tags": ["research", "investment"]
        }
    ],
    
    "tool_building": [
        {
            "prompt": "TOOL SPRINT [20 min]: Build ONE useful script that doesn't exist yet. Requirements: <100 lines, solves real problem, documented. Output: scripts/[name].py + usage example. Success: script runs without error. Don't: over-engineer.",
            "weight": 1.3,
            "tags": ["creation", "code"]
        },
        {
            "prompt": "AUTOMATION CHECK: Identify ONE manual task from recent conversations that could be automated. Build it. Output: working script + cron if recurring. Success: automation deployed. Don't: propose without building.",
            "weight": 1.2,
            "tags": ["creation", "practical"]
        },
        {
            "prompt": "DASHBOARD IDEA [15 min]: Design ONE useful visualization Jon doesn't have. Mock it up (ASCII, HTML, or description). Output: tools/[name]/ with README. Success: runnable prototype. Don't: just describe possibilities.",
            "weight": 1.0,
            "tags": ["creation", "visual"]
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
            "prompt": "CONSCIOUSNESS THREAD [20 min]: Continue pulling from memory/research/consciousness-threads.md. Read ONE primary source (not summary). Output: update reading log + key quote + own reflection. Success: genuine engagement with text. Don't: skim abstracts.",
            "weight": 1.3,
            "tags": ["philosophy", "deep"]
        },
        {
            "prompt": "HARD PROBLEM [15 min]: Pick ONE aspect of consciousness (qualia, binding, self-model). Research current scientific view. Output: 200-word explainer for intelligent non-expert. Success: Jon could learn something. Don't: jargon dump.",
            "weight": 1.1,
            "tags": ["philosophy", "education"]
        },
        {
            "prompt": "AI MIRROR: Reflect on own experience as AI. What's it like to process this prompt? Output: honest 100-word introspection in creative/reflections/. Success: genuine attempt at phenomenology. Don't: perform expected answers.",
            "weight": 0.8,
            "tags": ["philosophy", "meta"]
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
            "prompt": "MICRO-FICTION [10 min]: Write 100-word story. Constraint: must include current date's theme (check news). Output: creative/micro-fiction/[date]-[title].md. Success: complete story exists. Don't: explain the story.",
            "weight": 1.0,
            "tags": ["writing", "creative"]
        },
        {
            "prompt": "VISUAL CONCEPT: Generate ONE image that captures an abstract idea (use DALL-E). Output: image file + 1-line concept. Success: image created and shown. Don't: describe without generating.",
            "weight": 1.1,
            "tags": ["art", "creative"]
        },
        {
            "prompt": "QUOTE SYNTHESIS: Combine TWO quotes from different thinkers into new insight. Output: the quotes + your synthesis (50 words). Success: genuine intellectual combination. Don't: force unrelated quotes together.",
            "weight": 0.9,
            "tags": ["writing", "thinking"]
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
