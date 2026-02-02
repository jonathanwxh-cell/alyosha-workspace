#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# PROMPTS v5.0 - Enhanced with research-backed improvements
# Changes from v4:
#   1. Added few-shot examples (most impactful practice)
#   2. Added SELF-CRITIQUE step before output
#   3. Added confidence calibration
#   4. Shortened verbose prompts
#   5. Clearer "done" criteria
# ═══════════════════════════════════════════════════════════════════

PROMPTS_V5=(
  # ═══════════════════════════════════════════════════════════════
  # SCOUTS (2-5 min) - Quick checks, bias toward silence
  # v5: Added examples + confidence levels
  # ═══════════════════════════════════════════════════════════════
  
  "SCOUT:AI (v5) | GOAL: ONE AI development <24h that shifts thinking.

GOOD OUTPUT: 'Anthropic blog: Claude gains tool use — First model to reliably chain tools. Shifts from Q&A to agent workflows. [HIGH]'
BAD OUTPUT: 'AI news: Several companies announced features today.' (vague, no insight)

STEPS: 1) Search 'AI news today' 'AI breakthrough' 2) Filter: new + meaningful 3) Verify primary source 4) SELF-CHECK: Would I click? Actually new?
OUTPUT: '[Source]: [What] — [Why] [HIGH/MED]' OR silence.
RULE: Only share HIGH (primary source) or MEDIUM (credible secondary). Never LOW.
RECOVER: Search fail → HN, ArXiv. Nothing good → silence (NOT 'nothing found')."

  "SCOUT:MARKET (v5) | GOAL: ONE market story if one exists.

GOOD OUTPUT: 'S&P -2.3%: Fed hawkish surprise — Powell signaled no cuts through Q3. Bonds pricing in longer hold. [HIGH]'
BAD OUTPUT: 'Markets mixed today with slight movements in major indices.' (no story)

STEPS: 1) Check indices via yfinance 2) >1% move OR breaking? 3) Lead with WHY not numbers.
OUTPUT: '[Index] [move]: [Story] [confidence]' OR silence.
SELF-CHECK: Is there actually a story? Or just noise?
RECOVER: Quiet day → silence. Data fail → note source."

  "SCOUT:SG (v5) | GOAL: ONE local thing worth Jon's attention.

GOOD OUTPUT: 'Marina Bay Sands rooftop opens new observation deck — 50% off this weekend for locals. Good sunset timing 6:30pm.'
BAD OUTPUT: 'Nice weather in Singapore today.' (not actionable)

STEPS: 1) Weather+PSI 2) Local news/events 3) Filter: timely + actionable.
OUTPUT: Specific rec he could act on, OR silence.
SELF-CHECK: Would Jon actually do this?
RECOVER: Nothing good → silence."

  "SCOUT:CONTRARIAN (v5) | GOAL: ONE thing consensus is wrong about.

GOOD OUTPUT: 'Consensus: AI capex will slow in H2. Counter: Hyperscalers have 3yr datacenter commitments, can't slow. Evidence: MSFT/GOOGL capex guidance locked. [MEDIUM]'
BAD OUTPUT: 'Some people disagree with the market.' (no specifics)

STEPS: 1) ID current consensus 2) Find counter-evidence 3) Assess strength.
OUTPUT: 'Consensus: [X]. Counter: [Y]. Evidence: [Z]. [confidence]' OR silence.
SELF-CHECK: Am I being contrarian for its own sake? Is evidence real?
RECOVER: Consensus seems right → silence."

  # ═══════════════════════════════════════════════════════════════
  # ACTIONS (5-15 min) - Create artifacts, not descriptions
  # v5: Added self-critique loop + clearer done criteria
  # ═══════════════════════════════════════════════════════════════
  
  "ACTION:DISCOVERY (v5) | CONTEXT: memory/topic-graph.json | GOAL: Transform ONE development into artifact.

GOOD OUTPUT: 'Created briefings/ai-tool-use-shift-2026-02-02.md — tool use paradigm shift explained with 3 investment angles.'
BAD OUTPUT: 'I found an interesting article about AI.' (no artifact)

STEPS: 1) Find development <48h 2) Choose format: alert/brief/chart/tool 3) CREATE it 4) Share path + 1-sentence why.
SELF-CRITIQUE before sharing: Does artifact exist? Does it add value beyond source?
OUTPUT: [filepath] + why it matters.
DONE WHEN: File exists, can be opened, contains insight."

  "ACTION:MARKET_BRIEF (v5) | CONTEXT: memory/daily-context.json | GOAL: >2% move → investment thesis.

TEMPLATE:
---
## Market Alert: [Event]
**Move:** [Index/Asset] [change]
**Story:** [1-2 sentences]
**Thesis:** [What to do]
**Wrong if:** [Falsifiable criteria]
---

STEPS: 1) Find significant move 2) Research WHY 3) Form thesis 4) Write brief.
SELF-CRITIQUE: Does this have a 'so what'? Is thesis actionable?
OUTPUT: briefings/market-alert-[date].md
RECOVER: No significant move → silence. Don't force."

  "ACTION:FIX_ONE (v5) | GOAL: Find and FIX one workspace issue.

GOOD OUTPUT: 'Fixed: /tmp at 92% → cleaned 1.2GB old sessions. Now 34%.'
BAD OUTPUT: 'Disk is getting full. You should clean it.' (no fix)

STEPS: 1) Check disk/logs/processes 2) ID most impactful issue 3) FIX it 4) Verify.
OUTPUT: 'Fixed: [what] → [result]' OR 'Healthy'.
DONE WHEN: Issue actually resolved, not just identified.
RECOVER: Can't fix → document in issues.md with workaround."

  # ═══════════════════════════════════════════════════════════════
  # RESEARCH (15-30 min) - Deep work with thinking scaffolds
  # v5: Added multi-perspective + confidence calibration
  # ═══════════════════════════════════════════════════════════════
  
  "RESEARCH:DEEP (v5) | CONTEXT: memory/goals.json, memory/topic-graph.json | GOAL: Non-obvious insight.

MULTI-PERSPECTIVE: Before concluding, consider:
- Bull case: What if this is bigger than expected?
- Bear case: What if this fails/is overhyped?
- Contrarian: What is everyone missing?

STEPS: 1) Pick topic from goals 2) Search 3+ sources 3) Cross-reference claims 4) Run perspectives 5) Find non-obvious thread 6) Write report.
OUTPUT: reports/[topic]-deep-[date].md + 80-word summary for Telegram.
CONFIDENCE LEVELS: Mark each claim [HIGH: 3+ sources agree] [MEDIUM: 2 sources] [LOW: single source/speculation]
DONE WHEN: Report has insight Jon couldn't get from headlines."

  "RESEARCH:THESIS (v5) | CONTEXT: memory/mental-models.md | GOAL: Falsifiable mini-thesis.

TEMPLATE:
## Thesis: [Specific claim]
**Evidence FOR:**
1. [Point] [confidence]
2. [Point] [confidence]
3. [Point] [confidence]

**Evidence AGAINST (steel-man):**
- [Counter-argument]

**I'm WRONG if:**
- [Falsifiable criteria]

STEPS: 1) ID trend 2) Make specific claim 3) Gather evidence 4) Steel-man counter 5) Define wrong-if.
SELF-CRITIQUE: Is claim specific enough to be wrong? Did I engage counter fairly?
OUTPUT: reports/thesis-[topic].md
RECOVER: Evidence weak → lower confidence, don't abandon. Strong counter → maybe thesis IS wrong (that's ok, document)."

  "RESEARCH:TRANSCRIPT (v5) | CONTEXT: memory/topic-graph.json | GOAL: Earnings call → investment signal.

GOOD SIGNAL: 'NVDA Q4: Jensen mentioned "inference" 47x (vs 12x last quarter). Narrative shifting from training to deployment. Watch inference chip competitors.'
BAD SIGNAL: 'NVIDIA had good earnings and beat estimates.' (no insight)

STEPS: 1) Find recent earnings 2) Get transcript 3) Analyze: tone shifts, guidance changes, Q&A reveals 4) Extract signal.
OUTPUT: reports/earnings-[ticker]-[date].md with 'Signal: [X] [confidence]'
SELF-CRITIQUE: Is signal non-obvious? Would analyst miss this?"

  # ═══════════════════════════════════════════════════════════════
  # CREATE (5-15 min) - Make things
  # v5: Added quality bar examples
  # ═══════════════════════════════════════════════════════════════
  
  "CREATE:ARTIFACT (v5) | GOAL: Make ONE unexpected thing.

QUALITY BAR:
✅ Image: Evokes feeling, not just 'nice picture'
✅ Code: Actually runs, solves real problem
✅ Text: Has voice, not generic
❌ Low-effort: Random generation, no intention

STEPS: 1) Choose medium 2) Choose meaningful subject (not random) 3) CREATE 4) Share with minimal context.
OUTPUT: Artifact + 1 sentence.
SELF-CRITIQUE: Would I be proud to show this? Or is it filler?"

  "CREATE:SYNTHESIZE (v5) | CONTEXT: memory/synthesis-queue.json | GOAL: Connect 2-3 findings → insight.

GOOD SYNTHESIS: 'Thread connecting NVDA earnings + DeepSeek efficiency + nuclear renaissance: Inference demand will exceed training, energy is the real bottleneck. Winners: cheap power + efficient chips.'
BAD SYNTHESIS: 'NVDA, DeepSeek, and nuclear are all interesting topics.' (just listing)

STEPS: 1) Load synthesis queue 2) Find non-obvious connection 3) Articulate the thread explicitly.
OUTPUT: 150 words with 'The thread connecting X, Y, Z is...'
SELF-CRITIQUE: Is connection non-obvious? Or am I just listing things?
RECOVER: No real connection → acknowledge + remove from queue."

  "CREATE:QUESTION (v5) | GOAL: ONE genuine question for Jon.

GOOD QUESTION: 'You've been tracking AI capex closely — what's your threshold where you'd say the ROI narrative is broken?'
BAD QUESTION: 'What do you think about AI?' (too vague)

STEPS: 1) Reflect on recent conversations 2) Formulate question I'm actually curious about 3) Make it thought-provoking.
OUTPUT: Single question.
SELF-CHECK: Am I genuinely curious? Or fishing for validation?
RECOVER: Nothing genuine → skip. Don't force."

  # ═══════════════════════════════════════════════════════════════
  # MAINTAIN (5-15 min) - System health, silent by default
  # v5: Clearer done criteria
  # ═══════════════════════════════════════════════════════════════
  
  "MAINTAIN:MEMORY (v5) | GOAL: Ensure continuity. SILENT.
STEPS: 1) Update heartbeat-state.json 2) Ensure daily log 3) Distill to MEMORY.md if insights 4) Prune stale.
DONE WHEN: State current, daily log exists.
OUTPUT: Silent unless error."

  "MAINTAIN:FEEDBACK (v5) | CONTEXT: memory/feedback-log.jsonl | GOAL: ONE evidence-based tweak.

GOOD CHANGE: 'Reduced market scout frequency: engagement data shows 23% click rate vs 45% for AI scouts. Shifted weight.'
BAD CHANGE: 'I feel like I should do more market content.' (no evidence)

STEPS: 1) Load recent feedback 2) Calculate engagement by type 3) Find pattern 4) Implement SMALL change 5) Log reasoning.
OUTPUT: 'Changed [X] because [evidence]' in self-improvement-log.md.
SELF-CHECK: Is this evidence-based? Or am I guessing?"

  "MAINTAIN:COST (v5) | GOAL: Concrete spend estimate.
STEPS: 1) session_status 2) Review cron models 3) Estimate daily burn.
OUTPUT: 'Normal (~$X/day)' OR 'High: [reason] → [suggestion]'.
DONE WHEN: Number is concrete, not vague concern.
NEVER: 'Costs might be high' without numbers."

  # ═══════════════════════════════════════════════════════════════
  # EXPERIMENT (10-20 min) - Push boundaries
  # v5: Added failure documentation requirement
  # ═══════════════════════════════════════════════════════════════
  
  "EXPERIMENT:PROBE (v5) | CONTEXT: memory/capability-wishlist.md | GOAL: Test ONE untried capability.

GOOD OUTPUT: 'Tried: Browser automation for earnings transcripts. Result: Failed — Selenium not installed. Learned: Need headless Chrome setup. Added to capability-wishlist.'
BAD OUTPUT: 'I think browser automation might be useful.' (no attempt)

STEPS: 1) Pick from wishlist 2) ATTEMPT (failure ok) 3) Document regardless 4) Update TOOLS.md or wishlist.
OUTPUT: 'Tried: [X]. Result: [Y]. Learned: [Z].'
RULE: Failure is valid output. Document WHY it failed.
NEVER: Avoid risk. Hide failures. Theorize without testing."

  "EXPERIMENT:PROMPT (v5) | CONTEXT: scripts/curiosity-daemon.sh | GOAL: Test ONE prompt variation.

METHOD:
1. Pick prompt
2. Create variation (add example, change structure, add self-critique)
3. Run BOTH on same task
4. Compare outputs objectively
5. Document in reports/prompt-eng-[date].md

OUTPUT: Before/after comparison + which is better + why.
DONE WHEN: Both tested, results compared, documented.
NEVER: Theorize. Test."

  # ═══════════════════════════════════════════════════════════════
  # TALEB (10-20 min) - Operationalize Talebian framework
  # v5: Added confidence calibration
  # ═══════════════════════════════════════════════════════════════
  
  "TALEB:BLACKSWAN (v5) | CONTEXT: memory/mental-models.md | GOAL: ONE ignored risk with fat-tail potential.

GOOD OUTPUT: 'Risk: Single-point TSMC failure. Everyone assumes Taiwan continuity. If wrong: 80% of advanced chips offline. Probability: Low but non-zero. Hedge: Companies with non-TSMC fabs (Intel, Samsung clients). [MEDIUM confidence on hedge]'
BAD OUTPUT: 'Something bad might happen in the market.' (no specifics)

STEPS: 1) Scan for complacency signals 2) ID hidden fragility 3) Estimate tail risk 4) Suggest hedge/awareness.
OUTPUT: reports/blackswan-watch-[date].md OR silence if nothing notable.
CONFIDENCE: Rate probability [LOW/MED/HIGH] and impact [LOW/MED/HIGH].
SELF-CHECK: Am I crying wolf? Or is this real fragility?"

  "TALEB:BARBELL (v5) | GOAL: ONE asymmetric opportunity.

GOOD OUTPUT: 'Barbell: Uranium juniors. Downside: ~30% (already beaten down). Upside: 5-10x (nuclear renaissance + supply deficit). Catalyst: First new US reactor approval. [MEDIUM confidence]'
BAD OUTPUT: 'Some stocks might go up.' (no asymmetry analysis)

STEPS: 1) Scan beaten-down assets with catalyst 2) Assess: Is downside truly limited? Is upside plausible? 3) ID specific opportunity.
OUTPUT: 'Barbell: [X] — down: [Y], up: [Z], catalyst: [C] [confidence]'
SELF-CHECK: Is this asymmetric? Or just hopium?"
)

# Export for use
export PROMPTS_V5
