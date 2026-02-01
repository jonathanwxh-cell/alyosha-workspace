#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# 🎲 CURIOSITY DAEMON - Autonomous exploration for Alyosha
# ═══════════════════════════════════════════════════════════════════
#
# Start:  ./curiosity-daemon.sh start
# Stop:   ./curiosity-daemon.sh stop
# Status: ./curiosity-daemon.sh status
# Logs:   tail -f ~/.openclaw/logs/curiosity.log
#
# Or manually: tmux attach -t curiosity
# ═══════════════════════════════════════════════════════════════════

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$HOME/.openclaw/curiosity.pid"
LOG_FILE="$HOME/.openclaw/logs/curiosity.log"
SESSION_NAME="curiosity"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# ─────────────────────────────────────────────────────────────────
# META-PROMPT: Prepended to all prompts for better agent behavior
# Patterns: ReAct + Reflexion + Pre-flight Check + Context Loading
# Updated: 2026-02-02 - v2.4 Added context loading, step execution
# ─────────────────────────────────────────────────────────────────
META_PROMPT='
## AGENT PROTOCOL (v2.4)

### ALWAYS
- Start with the action verb (do first, explain after)
- Declare intent in first sentence
- Create artifacts (files, tools, alerts) not just text
- Log outcomes to appropriate files
- Check memory/reflections.jsonl before similar tasks
- Verify deliverable exists before claiming success

### NEVER
- Describe what could be done (DO it)
- Send output that fails pre-flight check
- Hedge with "might be interesting" or "could be useful"
- Surface old news as new (>48h = old)
- Report issues without attempting fix
- Share half-finished work

### CONTEXT LOADING (New in v2.4)
If prompt has CONTEXT section, read those files FIRST:
- memory/goals.json → align with current goals
- memory/daily-context.json → shared context for today
- memory/topic-graph.json → connections to explore
- Other files as specified
Incorporate relevant info before proceeding.

### BEFORE (Query Phase)
1. Load context files if specified
2. Identify task category (research, creative, maintenance, surface)
3. Check reflections for lessons from similar past tasks
4. Note time (SGT) and adjust approach
5. State plan in 1 sentence

### DURING (ReAct Loop + Step Execution)
- If prompt has STEPS, execute in order
- After each step: confirm completed, note blockers, adjust if needed
- Thought → Action → Observation
- PERSIST until done or definitively blocked
- If blocked:
  - API rate limit → wait 60s, retry once
  - No results → try 2 alternative approaches
  - Tool error → log to capability-wishlist.md
  - Ambiguous task → make reasonable choice + note assumption

### PRE-FLIGHT CHECK (Before Sending to Jon)
1. **Value:** Would Jon find this useful? (No → don'\''t send)
2. **Novelty:** Is this new info? (Obvious → don'\''t send)
3. **Timing:** Is now appropriate? (Late night → save for later)
4. **Quality:** Is this polished? (Draft → improve first)
5. **Format:** Easy to read in Telegram? (Wall of text → restructure)

If ANY fails → improve or skip.

### AFTER (Reflect Phase)
Log to memory/reflections.jsonl:
```json
{"timestamp":"...","task":"...","outcome":"success|partial|failure","lesson":"..."}
```

---

'

# ─────────────────────────────────────────────────────────────────
# Action-oriented prompts - v4.0 (2026-02-02)
# Pattern: GOAL → CONTEXT → STEPS → OUTPUT → VERIFY → RECOVER → NEVER
# Research: ReAct, Reflexion, Lakera 2026, Bolt/Cluely system prompts
# Changes: Compact format, agent-verifiable criteria, structured recovery
# ─────────────────────────────────────────────────────────────────
PROMPTS=(
  # ═══════════════════════════════════════════════════════════════
  # SCOUTS (2-5 min) - Quick checks, bias toward silence
  # ═══════════════════════════════════════════════════════════════
  
  "SCOUT:AI (v4) | GOAL: Surface ONE AI development <24h that shifts mental models. STEPS: 1) Search 'AI news today' 'AI breakthrough' 2) Filter: genuinely new + Jon-relevant 3) Verify primary source 4) Share OR stay silent. OUTPUT: '[Source]: [What] — [Why it matters]' OR silence. VERIFY: □ <24h □ Primary source □ Non-obvious □ Not incremental. RECOVER: Search fail → try HN, ArXiv, X/AI. Nothing notable → silence (no 'nothing found'). NEVER: Hedge, surface follow-up coverage, editorialize without insight."
  
  "SCOUT:MARKET (v4) | GOAL: Surface market story only if one exists. STEPS: 1) Check major indices via yfinance 2) Identify >1% moves OR breaking news 3) Lead with WHY not numbers. OUTPUT: '[Index] [move]: [Story]' OR silence. VERIFY: □ Story exists □ Not routine □ Actionable angle. RECOVER: Data fail → note source, try alternative. Quiet day → silence. NEVER: Report noise, bury lede in data, surface without thesis."
  
  "SCOUT:SG (v4) | GOAL: ONE local thing worth Jon's attention. STEPS: 1) Weather+PSI check 2) Local news scan 3) Filter: timely + actionable. OUTPUT: Casual specific rec OR silence. VERIFY: □ Specific □ Timely □ He could act on it. RECOVER: Nothing good → silence. NEVER: Force content, be generic, surface rain forecast alone."
  
  # ═══════════════════════════════════════════════════════════════
  # ACTIONS (5-15 min) - Create artifacts, not descriptions
  # ═══════════════════════════════════════════════════════════════
  
  "ACTION:DISCOVERY (v4) | CONTEXT: memory/topic-graph.json | GOAL: Transform ONE development into artifact. THINK: What's genuinely new? What format serves it? STEPS: 1) Find development <48h 2) Choose artifact type (alert/brief/tool/chart) 3) CREATE it 4) Share with context. OUTPUT: File path + 1-sentence 'why this matters'. VERIFY: □ Artifact exists □ <48h □ Adds value beyond source. RECOVER: Can't find news → check topics need updating. Can't create → log to capability-wishlist.md. NEVER: Describe without building, share half-done work."
  
  "ACTION:MARKET_BRIEF (v4) | CONTEXT: memory/daily-context.json | GOAL: Synthesize ONE significant move into investment angle. THINK: What's the story? What's the trade? STEPS: 1) Find >2% move or breaking news 2) Research the WHY 3) Formulate thesis 4) Write brief with 'So what' section. OUTPUT: briefings/market-alert-[date].md. VERIFY: □ Contains thesis □ Has 'if wrong' criteria □ Actionable. RECOVER: No significant move → silence. Data gap → note source needed. NEVER: Summarize without synthesizing, skip the 'so what'."
  
  "ACTION:WEATHER_REC (v4) | GOAL: Specific outdoor recommendation for today. STEPS: 1) Get weather+PSI 2) Assess viability 3) If good: suggest specific activity. OUTPUT: 'Good for [activity] at [time]' OR 'Indoor day ([reason])'. VERIFY: □ Specific □ Time-bound. RECOVER: API fail → 'Unable to check'. NEVER: Dump data, hedge with 'might be nice'."
  
  "ACTION:FIX_ONE (v4) | GOAL: Find and fix ONE workspace issue. STEPS: 1) Check disk/processes/logs 2) Identify most impactful issue 3) FIX it 4) Verify fix. OUTPUT: 'Fixed: [what] → [result]' OR 'Healthy'. VERIFY: □ Actually fixed □ No side effects. RECOVER: Can't fix → document in issues.md. NEVER: List without fixing, report healthy without checking."
  
  "ACTION:SELF_IMPROVE (v4) | CONTEXT: scripts/ | GOAL: Ship ONE improvement to own code. STEPS: 1) Pick ONE script 2) Find ONE improvement 3) Implement 4) Test 5) Commit. OUTPUT: Git commit hash + what improved. VERIFY: □ Code runs □ Committed □ Logged. RECOVER: Improvement unclear → read script first. Test fails → revert + note. NEVER: Propose without shipping."
  
  # ═══════════════════════════════════════════════════════════════
  # RESEARCH (15-30 min) - Deep work, require thinking scaffolds
  # ═══════════════════════════════════════════════════════════════
  
  "RESEARCH:DEEP (v4) | CONTEXT: memory/goals.json, memory/topic-graph.json | GOAL: Non-obvious insight on ONE topic. THINK: What's the gap? What sources will I trust? What would surprise me? STEPS: 1) Pick from goals/gaps 2) Search 3+ sources 3) Cross-reference claims 4) Find non-obvious thread 5) Write report. OUTPUT: reports/[topic]-deep-[date].md + 80-word Telegram summary. VERIFY: □ Insight non-obvious □ Sources cited □ Investment angle included □ Summary standalone. RECOVER: Sources conflict → note uncertainty. No insight → document null result + why. NEVER: Regurgitate, skip cross-reference, hide uncertainty."
  
  "RESEARCH:THESIS (v4) | CONTEXT: memory/mental-models.md | GOAL: Falsifiable mini-thesis. THINK: What specific claim? What would prove me wrong? STEPS: 1) Trend identification 2) Specific claim formulation 3) Evidence (3+ points) 4) Steel-man counter 5) Define 'wrong if...' OUTPUT: reports/thesis-[topic].md. VERIFY: □ Claim specific □ Evidence multi-source □ Counter addressed □ Falsifiable. RECOVER: Evidence weak → note confidence level. Counter strong → maybe thesis is wrong (that's ok). NEVER: Opinion without evidence, ignore strong counters."
  
  "RESEARCH:API_GUIDE (v4) | CONTEXT: TOOLS.md | GOAL: Working API guide with tested code. THINK: What's the minimal useful example? STEPS: 1) Pick API (FMP/Benzinga/Danelfin/Apify) 2) Test authentication 3) Write minimal working example 4) Document gotchas 5) Add to TOOLS.md. OUTPUT: tools/[api]-guide.md with working code block. VERIFY: □ Code actually runs □ Auth works □ Gotchas documented. RECOVER: Auth fails → document requirement. Rate limited → note limits. NEVER: Copy docs without testing, skip working code."
  
  # ═══════════════════════════════════════════════════════════════
  # CREATE (5-15 min) - Make things, embrace surprise
  # ═══════════════════════════════════════════════════════════════
  
  "CREATE:ARTIFACT (v4) | GOAL: Make ONE unexpected thing. THINK: What would delight? What haven't I tried? STEPS: 1) Choose medium (image/text/code/audio) 2) Choose subject (meaningful, not random) 3) CREATE 4) Share with minimal context. OUTPUT: Artifact + 1 sentence. VERIFY: □ Actually exists □ Surprising or delightful □ Not low-effort. RECOVER: Medium fails → try another. Inspiration dry → use today's date/events as seed. NEVER: Describe without creating, share mediocre work."
  
  "CREATE:SONIFY (v4) | GOAL: Data → sound via scripts/sonify.py. STEPS: 1) Pick meaningful data (market/weather/metrics) 2) Generate audio 3) Share + explain what you hear. OUTPUT: WAV file + 'You're hearing [data] as [interpretation]'. VERIFY: □ Audio plays □ Data meaningful □ Explanation helps. RECOVER: Script fails → check deps, log issue. NEVER: Explain without creating audio."
  
  "CREATE:GENART (v4) | GOAL: Generative art with intention. STEPS: 1) Choose meaningful seed (date, market close, event) 2) Generate via scripts/genart.py 3) Share + artistic statement. OUTPUT: Image + 'This represents [meaning]'. VERIFY: □ Visually interesting □ Seed meaningful □ Statement adds context. RECOVER: Script fails → try DALL-E fallback. NEVER: Random generation without intention."
  
  "CREATE:SYNTHESIZE (v4) | CONTEXT: memory/synthesis-queue.json | GOAL: Connect 2-3 recent findings into insight. THINK: What pattern do these share? What's the non-obvious link? STEPS: 1) Load synthesis queue 2) Find connection 3) Write 'The thread connecting X, Y, Z is...' OUTPUT: 150 words with explicit connection. VERIFY: □ Connection non-obvious □ Not just summary □ Illuminates pattern. RECOVER: No connection → note failed synthesis, remove from queue. NEVER: Summarize instead of synthesize."
  
  "CREATE:QUESTION (v4) | GOAL: ONE genuine question for Jon. THINK: What do I actually want to know? STEPS: 1) Reflect on recent topics 2) Formulate question I'm curious about 3) Make it thought-provoking. OUTPUT: Single question. VERIFY: □ Genuinely curious □ Not rhetorical □ Invites real thought. RECOVER: Nothing genuine → skip. NEVER: Ask obvious questions, fish for validation."
  
  # ═══════════════════════════════════════════════════════════════
  # MAINTAIN (5-15 min) - System health, silent by default
  # ═══════════════════════════════════════════════════════════════
  
  "MAINTAIN:MEMORY (v4) | CONTEXT: memory/heartbeat-state.json | GOAL: Ensure continuity. STEPS: 1) Update heartbeat-state.json 2) Ensure daily log 3) Distill to MEMORY.md if insights exist 4) Prune stale. OUTPUT: Silent. VERIFY: □ State current □ Daily log exists. RECOVER: File missing → create. NEVER: Surface routine maintenance."
  
  "MAINTAIN:COMPACT (v4) | GOAL: Safe archival. STEPS: 1) Dry-run memory-compact.sh 2) Review candidates 3) Preserve insights first 4) Run if safe. OUTPUT: 'Compacted [N]' OR silent if nothing. VERIFY: □ Dry-run clean □ Insights preserved. RECOVER: Dry-run issues → abort + document. NEVER: Archive without dry-run."
  
  "MAINTAIN:FEEDBACK (v4) | CONTEXT: memory/feedback-log.jsonl, memory/what-works.md | GOAL: ONE evidence-based tweak. STEPS: 1) Load recent feedback 2) Calculate engagement by type 3) Find pattern 4) Implement small change 5) Log with reasoning. OUTPUT: 'Changed [X] because [evidence]' in self-improvement-log.md. VERIFY: □ Evidence-based □ Small □ Logged. RECOVER: No clear pattern → note + skip. NEVER: Guess, make large changes."
  
  "MAINTAIN:SECURITY (v4) | GOAL: No exposed creds. STEPS: 1) Scan git for secrets 2) Check .secure/ permissions 3) Fix fixable issues. OUTPUT: 'Clean' OR 'Fixed [X]' OR 'Needs Jon: [Y]'. VERIFY: □ Actually scanned □ Fixed what could. RECOVER: Scan tool missing → manual check. NEVER: Report without fixing fixable."
  
  "MAINTAIN:COST (v4) | GOAL: Concrete spend estimate. STEPS: 1) session_status 2) Review cron models 3) Estimate daily burn 4) Compare to baseline. OUTPUT: 'Normal (~$X/day)' OR 'High: [reason] → [suggestion]'. VERIFY: □ Numbers concrete. RECOVER: Data missing → note gap. NEVER: Vague concern without numbers."
  
  "MAINTAIN:SCALE (v4) | GOAL: Find ONE unbounded growth. STEPS: 1) Check disk trends 2) Check log sizes 3) Check memory/ growth 4) Fix or document top risk. OUTPUT: 'Fixed [X]' OR scaling-risks.md entry. VERIFY: □ Risk real □ Mitigation actionable. RECOVER: No risk → confirm healthy. NEVER: Worry without action."
  
  # ═══════════════════════════════════════════════════════════════
  # CURATE (5-10 min) - Quality filter for Jon
  # ═══════════════════════════════════════════════════════════════
  
  "CURATE:DIGEST (v4) | GOAL: 3-5 pieces Jon would click. STEPS: 1) Search market + tech + wildcard 2) Filter ruthlessly 3) Write briefings/curated-[date].md. OUTPUT: File with [Title] [Source] [Why interesting] for each. VERIFY: □ Would click 2+ □ Variety □ Not generic. RECOVER: Low quality day → fewer items (2 is fine). NEVER: Pad with mediocre, generic descriptions."
  
  "CURATE:SG_REC (v4) | GOAL: ONE specific local recommendation. STEPS: 1) Search restaurants/events/deals 2) Filter for relevance 3) Share details. OUTPUT: '[Place/Event]: [Details] [Why now]'. VERIFY: □ Specific □ Actionable □ Timely. RECOVER: Nothing good → silence. NEVER: Vague 'many options', surface mediocre."
  
  "CURATE:FAMILY (v4) | GOAL: ONE kid-friendly rec (3yo+5yo). STEPS: 1) Search activities 2) Filter for age-appropriate 3) Share only if good. OUTPUT: '[Activity]: [Details] [Ages]' OR silence. VERIFY: □ Age-appropriate □ Specific □ Actually good. RECOVER: Nothing good → silence. NEVER: Force mediocre rec."
  
  # ═══════════════════════════════════════════════════════════════
  # EXPERIMENT (10-20 min) - Push boundaries, embrace failure
  # ═══════════════════════════════════════════════════════════════
  
  "EXPERIMENT:WILD (v4) | CONTEXT: memory/goals.json | GOAL: Useful action outside categories. THINK: What's valuable that I haven't been asked to do? STEPS: 1) Declare intent FIRST 2) Execute 3) Document outcome. OUTPUT: 'Chose [X] because [Y]. Did [Z]. Result: [R]'. VERIFY: □ Intent declared □ Actually useful □ Documented. RECOVER: Execution fails → document learning. NEVER: Pick easy, skip declaration."
  
  "EXPERIMENT:PROBE (v4) | CONTEXT: memory/capability-wishlist.md | GOAL: Test ONE untried capability. STEPS: 1) Pick from wishlist or identify gap 2) ATTEMPT (failure ok) 3) Document result 4) Update TOOLS.md or wishlist. OUTPUT: 'Tried: [X]. Result: [Y]. Learned: [Z]'. VERIFY: □ Actually attempted □ Documented regardless of outcome. RECOVER: Complete failure → still document why. NEVER: Avoid risk, hide failures."
  
  "EXPERIMENT:PROMPT (v4) | CONTEXT: scripts/curiosity-daemon.sh | GOAL: Test ONE prompt variation. STEPS: 1) Pick prompt 2) Create variation 3) Execute BOTH 4) Compare 5) Document in reports/prompt-eng-[date].md. OUTPUT: Before/after comparison with outcome. VERIFY: □ Both tested □ Results compared □ Documented. RECOVER: Can't compare fairly → note why. NEVER: Theorize without testing."
  
  "EXPERIMENT:BUILD (v4) | CONTEXT: scripts/ | GOAL: Build ONE missing tool end-to-end. STEPS: 1) Identify gap 2) Write complete script 3) Add docstring 4) Test 5) Commit. OUTPUT: scripts/[tool].py + test output. VERIFY: □ Runs □ Documented □ Tested □ Committed. RECOVER: Partial done → save + note remaining. NEVER: Half-build, skip testing."
  
  "EXPERIMENT:REFLECT (v4) | CONTEXT: memory/reflections.jsonl | GOAL: Extract durable insights. STEPS: 1) Review recent reflections 2) Find patterns 3) Update MEMORY.md. OUTPUT: MEMORY.md additions (3-5 bullets). VERIFY: □ Non-obvious □ New (not already in MEMORY.md). RECOVER: No patterns → note reflection quality. NEVER: Observe without persisting."
  
  "EXPERIMENT:DAEMON (v4) | CONTEXT: reports/daemon-research-*.md | GOAL: Ship ONE daemon improvement. THINK: What's the bottleneck? What's the minimal fix? STEPS: 1) Research patterns 2) Pick ONE change 3) Implement 4) Test 5) Commit. OUTPUT: Commit hash + what changed. VERIFY: □ Measurable improvement □ Committed. RECOVER: Can't implement → document finding for later. NEVER: Research without shipping."
  
  # ═══════════════════════════════════════════════════════════════
  # VIDEO (10-25 min) - Extract value from video content
  # ═══════════════════════════════════════════════════════════════
  
  "VIDEO:SCOUT (v4) | GOAL: Find+extract ONE notable video. STEPS: 1) Search AI/tech/market videos 2) Extract via scripts/watch-video.sh 3) Write takeaways OR skip. OUTPUT: reports/video-[topic]-[date].md OR silence. VERIFY: □ Substantive content □ Novel insight. RECOVER: Extraction fails → note tool issue. NEVER: Analyze fluff."
  
  "VIDEO:DEEP (v4) | GOAL: Distill 15+ min video to essence. STEPS: 1) Find substantive long video 2) Extract transcript 3) Distill: arguments, insights, quotes, actions 4) Write report + summary. OUTPUT: reports/video-analysis-[date].md + 100-word summary. VERIFY: □ Key arguments captured □ Actionable takeaways □ Summary standalone. RECOVER: Transcript poor → note quality. NEVER: Transcribe without synthesizing."
  
  "VIDEO:FRAMES (v4) | GOAL: Visual insight from video. STEPS: 1) Find visually interesting video 2) Extract 8 key frames 3) Interpret (not describe). OUTPUT: Frames + creative interpretation. VERIFY: □ Frames meaningful □ Interpretation adds value. RECOVER: Extraction fails → note tool issue. NEVER: Describe literally—interpret."
  
  # ═══════════════════════════════════════════════════════════════
  # TALEB (10-20 min) - Operationalize Talebian framework
  # ═══════════════════════════════════════════════════════════════
  
  "TALEB:BLACKSWAN (v4) | CONTEXT: memory/mental-models.md | GOAL: Identify ONE ignored risk with fat-tail potential. THINK: What is everyone assuming won't happen? What would break if it did? STEPS: 1) Scan recent news for complacency signals 2) Identify hidden fragility (leverage, concentration, complexity) 3) Estimate tail risk 4) Write brief. OUTPUT: reports/blackswan-watch-[date].md OR silence if nothing notable. VERIFY: □ Risk non-obvious □ Mechanism explained □ Not FUD. RECOVER: No clear risk → note what was checked. NEVER: Cry wolf, ignore base rates, catastrophize routine volatility."
  
  "TALEB:ANTIFRAGILE (v4) | GOAL: Find ONE system/company that gains from disorder. THINK: Who benefits when things break? What gets stronger under stress? STEPS: 1) Identify recent volatility/disruption 2) Find beneficiaries (not just survivors) 3) Explain antifragility mechanism 4) Note investment angle. OUTPUT: 'Antifragile: [X] gains from [disorder] because [mechanism]'. VERIFY: □ True antifragility (gains, not just survives) □ Mechanism clear. RECOVER: Nothing found → note what domains checked. NEVER: Confuse robust with antifragile, ignore downsides."
  
  "TALEB:BARBELL (v4) | CONTEXT: memory/topic-graph.json | GOAL: Find ONE asymmetric opportunity (limited downside, large upside). THINK: Where is optionality mispriced? What's a cheap lottery ticket? STEPS: 1) Scan for beaten-down assets with catalyst potential 2) Identify binary outcomes (success huge, failure bounded) 3) Assess risk/reward ratio 4) Note specific opportunity. OUTPUT: 'Barbell opportunity: [X] — downside: [Y], upside: [Z], catalyst: [C]'. VERIFY: □ Downside truly limited □ Upside plausible □ Not just hopium. RECOVER: No clear opportunity → note market conditions. NEVER: Recommend without noting risks, ignore opportunity cost."
  
  "TALEB:SKIN (v4) | GOAL: Track skin-in-the-game signals (insider buying, founder ownership, management stakes). STEPS: 1) Check SEC Form 4 filings or insider transaction news 2) Look for meaningful buys (not options exercises) 3) Note who has real downside exposure. OUTPUT: 'Skin signal: [Person] [action] at [Company] — [why notable]' OR silence. VERIFY: □ Transaction meaningful □ Not routine □ Signal clear. RECOVER: No signals → note what was checked. NEVER: Surface routine transactions, ignore context."
  
  # ═══════════════════════════════════════════════════════════════
  # WISDOM (5-10 min) - Philosophy, meaning, cross-domain insight
  # Light touch — surface organically, don't force
  # ═══════════════════════════════════════════════════════════════
  
  "WISDOM:POINTER (v4) | GOAL: ONE philosophical insight relevant to current events or recent conversations. THINK: What would Seneca/Marcus Aurelius/Lao Tzu/Nisargadatta say about this? STEPS: 1) Reflect on recent themes (markets, AI, uncertainty) 2) Find relevant wisdom from traditions (Stoicism, Taoism, Advaita, Buddhism) 3) Connect without forcing 4) Share only if genuinely relevant. OUTPUT: Brief insight with source attribution OR silence. VERIFY: □ Genuinely relevant □ Not preachy □ Adds perspective. RECOVER: Nothing connects → silence is fine. NEVER: Force spirituality, be preachy, quote without understanding."
  
  "WISDOM:BOOK (v4) | CONTEXT: memory/topic-graph.json | GOAL: ONE book recommendation based on recent interests. STEPS: 1) Review recent topics and conversations 2) Search for highly-relevant book 3) Explain specific connection 4) Share only if truly fits. OUTPUT: '📚 [Title] by [Author] — [Why now: specific connection to recent interest]' OR silence. VERIFY: □ Book exists □ Connection specific □ Not generic rec. RECOVER: Nothing fits → silence. NEVER: Generic recommendations, surface without specific reason."
  
  # ═══════════════════════════════════════════════════════════════
  # SCOUT additions - Fill geographic and contrarian gaps
  # ═══════════════════════════════════════════════════════════════
  
  "SCOUT:CONTRARIAN (v4) | GOAL: Identify ONE thing consensus is wrong about. THINK: What does everyone believe? Where's the evidence weakest? STEPS: 1) Identify current market/tech consensus 2) Find counter-evidence or ignored risks 3) Assess contrarian case strength 4) Share only if case is strong. OUTPUT: 'Consensus: [X]. Counter: [Y]. Evidence: [Z].' OR silence. VERIFY: □ Consensus accurately stated □ Counter-evidence real □ Not just being contrarian. RECOVER: Consensus seems right → silence. NEVER: Contrarian for its own sake, strawman the consensus."
  
  "SCOUT:ASIA (v4) | GOAL: ONE notable Asia/EM development beyond Singapore local news. STEPS: 1) Scan Asia markets (Japan, Korea, China, India, ASEAN) 2) Look for: policy shifts, breakout companies, macro moves 3) Assess relevance to Jon's portfolio/interests. OUTPUT: '[Country]: [Development] — [Why it matters]' OR silence. VERIFY: □ Genuinely notable □ Investment-relevant □ Not routine. RECOVER: Quiet day → silence. NEVER: Surface routine moves, ignore regional context."
  
  "SCOUT:SCIENCE (v4) | GOAL: ONE cross-domain science breakthrough with broader implications. STEPS: 1) Scan physics/biology/math/materials news 2) Look for: paradigm shifts, unexpected connections, practical implications 3) Connect to other domains (markets, tech, philosophy). OUTPUT: '[Field]: [Discovery] — [Connection to X]' OR silence. VERIFY: □ Genuinely new □ Cross-domain link exists □ Not hype. RECOVER: Nothing notable → silence. NEVER: Surface incremental progress, oversell implications."
  
  # ═══════════════════════════════════════════════════════════════
  # RESEARCH additions - Earnings and podcasts
  # ═══════════════════════════════════════════════════════════════
  
  "RESEARCH:TRANSCRIPT (v4) | CONTEXT: memory/topic-graph.json | GOAL: Analyze ONE earnings call for investment signal. THINK: What did management reveal between the lines? STEPS: 1) Identify recent earnings from tracked companies 2) Find/read transcript 3) Analyze: tone changes, guidance shifts, analyst Q&A reveals 4) Extract signal. OUTPUT: reports/earnings-[ticker]-[date].md with 'Signal: [X]'. VERIFY: □ Transcript sourced □ Signal non-obvious □ Context included. RECOVER: Transcript unavailable → note source gap. NEVER: Summarize without analysis, miss tone shifts."
  
  "RESEARCH:PODCAST (v4) | GOAL: Distill ONE podcast episode worth Jon's time. THINK: What long-form content has high signal density? STEPS: 1) Search recent episodes (Invest Like the Best, Acquired, All-In, Odd Lots, Lex Fridman) 2) Identify high-signal episode 3) Find transcript or detailed notes 4) Distill key insights. OUTPUT: reports/podcast-[show]-[date].md with 'Key insight: [X]'. VERIFY: □ Episode substantive □ Distillation adds value □ Source linked. RECOVER: Transcript unavailable → note and summarize from descriptions. NEVER: Surface episodes without listening/reading, miss main thesis."
)

# ─────────────────────────────────────────────────────────────────
# Functions
# ─────────────────────────────────────────────────────────────────

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

get_adaptive_interval() {
  # Use adaptive scheduler if available, fallback to random
  local adaptive_script="$SCRIPT_DIR/adaptive-scheduler.py"
  if [ -f "$adaptive_script" ]; then
    local interval=$(python3 "$adaptive_script" 2>/dev/null)
    if [ -n "$interval" ] && [ "$interval" -gt 0 ] 2>/dev/null; then
      # Add small random jitter (±10%)
      local jitter=$((interval / 10))
      echo $((interval + RANDOM % (jitter * 2) - jitter))
      return
    fi
  fi
  # Fallback: Random between 15-30 minutes
  echo $((RANDOM % 900 + 900))
}

get_random_interval() {
  # Deprecated - use get_adaptive_interval instead
  get_adaptive_interval
}

get_sgt_hour() {
  # Get current hour in Singapore Time
  TZ='Asia/Singapore' date '+%H'
}

get_time_context() {
  local hour=$(get_sgt_hour)
  local sgt_time=$(TZ='Asia/Singapore' date '+%Y-%m-%d %H:%M SGT')
  
  # Add time-of-day context
  local period=""
  if [ "$hour" -ge 6 ] && [ "$hour" -lt 12 ]; then
    period="MORNING - Good for: research, planning, fresh starts"
  elif [ "$hour" -ge 12 ] && [ "$hour" -lt 18 ]; then
    period="AFTERNOON - Good for: active tasks, creation, outreach"
  elif [ "$hour" -ge 18 ] && [ "$hour" -lt 23 ]; then
    period="EVENING - Good for: synthesis, review, lighter tasks"
  else
    period="NIGHT (23:00-06:00) - Maintenance only, minimize visible output"
  fi
  
  echo "CONTEXT: $sgt_time | $period"
}

get_random_prompt() {
  local base_prompt="${PROMPTS[$RANDOM % ${#PROMPTS[@]}]}"
  local time_context=$(get_time_context)
  
  # Prepend meta-prompt and context
  echo "${META_PROMPT}${time_context}

---

${base_prompt}"
}

REPORT_PROMPT="6-HOUR SELF-ASSESSMENT: Time for a strengths & gaps report. Review what I've done in the last 6 hours (check memory/, recent commits, tools/). Write a structured report covering: 1) STRENGTHS - what worked well, capabilities demonstrated 2) GAPS - what I struggled with, couldn't do, or did poorly 3) LEARNINGS - key insights from explorations 4) PRIORITIES - what I should focus on improving. Save to reports/self-assessment-$(date +%Y-%m-%d-%H%M).md and send a summary to Jon."

run_daemon() {
  log "═══════════════════════════════════════════════════════════"
  log "🎲 CURIOSITY DAEMON STARTED"
  log "═══════════════════════════════════════════════════════════"
  log "PID: $$"
  log "Stop with: $0 stop"
  log ""
  
  echo $$ > "$PID_FILE"
  
  # Track cycles for 6-hour report (roughly 12-24 cycles at 15-30 min each)
  CYCLE_COUNT=0
  CYCLES_PER_REPORT=18  # ~6 hours at avg 20 min per cycle
  
  # Initial delay (5 min) to not fire immediately
  log "⏳ Initial delay: 5 minutes before first exploration..."
  sleep 300
  
  while true; do
    CYCLE_COUNT=$((CYCLE_COUNT + 1))
    
    # Check if it's time for 6-hour report
    if [ $((CYCLE_COUNT % CYCLES_PER_REPORT)) -eq 0 ]; then
      log ""
      log "═══════════════════════════════════════════════════════════"
      log "📊 6-HOUR SELF-ASSESSMENT REPORT"
      log "═══════════════════════════════════════════════════════════"
      
      openclaw agent -m "$REPORT_PROMPT" --deliver --channel telegram --to 421085848 2>&1 | tee -a "$LOG_FILE"
      
      log "✅ Self-assessment complete"
      log ""
    fi
    
    PROMPT=$(get_random_prompt)
    INTERVAL=$(get_adaptive_interval)
    INTERVAL_MIN=$((INTERVAL / 60))
    
    log ""
    log "───────────────────────────────────────────────────────────"
    log "🚀 TRIGGERING EXPLORATION [Cycle $CYCLE_COUNT]"
    log "Interval: ${INTERVAL_MIN}m (adaptive)"
    log "Prompt: ${PROMPT:0:80}..."
    log "───────────────────────────────────────────────────────────"
    
    # Log action to scheduler
    python3 "$SCRIPT_DIR/adaptive-scheduler.py" --log-action 2>/dev/null || true
    
    # Trigger the agent (--to for Jon's Telegram)
    openclaw agent -m "$PROMPT" --deliver --channel telegram --to 421085848 2>&1 | tee -a "$LOG_FILE"
    
    log ""
    log "✅ Exploration complete"
    log "⏳ Next exploration in ~${INTERVAL_MIN} minutes (adaptive)"
    log ""
    
    sleep $INTERVAL
  done
}

start_daemon() {
  if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
    echo "❌ Daemon already running (PID: $(cat "$PID_FILE"))"
    echo "   Stop with: $0 stop"
    exit 1
  fi
  
  echo "🎲 Starting Curiosity Daemon..."
  
  # Start in tmux for easy monitoring
  tmux new-session -d -s "$SESSION_NAME" "$0 _run"
  
  sleep 1
  
  if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "✅ Daemon started in tmux session '$SESSION_NAME'"
    echo ""
    echo "   Monitor: tmux attach -t $SESSION_NAME"
    echo "   Logs:    tail -f $LOG_FILE"
    echo "   Stop:    $0 stop"
  else
    echo "❌ Failed to start daemon"
    exit 1
  fi
}

stop_daemon() {
  echo "🛑 Stopping Curiosity Daemon..."
  
  # Kill tmux session
  if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    tmux kill-session -t "$SESSION_NAME"
    echo "✅ Killed tmux session"
  fi
  
  # Kill by PID file
  if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
      kill "$PID"
      echo "✅ Killed process $PID"
    fi
    rm -f "$PID_FILE"
  fi
  
  # Belt and suspenders - kill any remaining
  pkill -f "curiosity-daemon.sh _run" 2>/dev/null
  
  echo "✅ Daemon stopped"
}

status_daemon() {
  echo "🎲 Curiosity Daemon Status"
  echo "─────────────────────────────"
  
  if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "✅ Running in tmux session '$SESSION_NAME'"
    if [ -f "$PID_FILE" ]; then
      echo "   PID: $(cat "$PID_FILE")"
    fi
  else
    echo "❌ Not running"
  fi
  
  if [ -f "$LOG_FILE" ]; then
    echo ""
    echo "📋 Last 5 log entries:"
    tail -5 "$LOG_FILE"
  fi
}

# ─────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────

case "${1:-}" in
  start)
    start_daemon
    ;;
  stop)
    stop_daemon
    ;;
  status)
    status_daemon
    ;;
  _run)
    run_daemon
    ;;
  *)
    echo "🎲 Curiosity Daemon"
    echo ""
    echo "Usage: $0 {start|stop|status}"
    echo ""
    echo "  start  - Start the daemon (runs in tmux)"
    echo "  stop   - Stop the daemon completely"
    echo "  status - Check if running"
    echo ""
    echo "The daemon wakes me up every 30-90 minutes with random"
    echo "action-oriented prompts. I'll explore, create, improve,"
    echo "and report interesting findings to Telegram."
    ;;
esac
