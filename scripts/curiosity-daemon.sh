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
# Action-oriented prompts - v3.0 (2026-02-02)
# Pattern: CONTEXT → GOAL → STEPS → OUTPUT → VERIFY → IF_BLOCKED → NEVER
# Research: ReAct, Reflexion, Lakera guide, context loading, step decomposition
# ─────────────────────────────────────────────────────────────────
PROMPTS=(
  # === QUICK SCOUTS (2-5 min) - Lean, fast checks ===
  
  "SCOUT: AI_NEWS (v3.0) | GOAL: Find ONE notable AI development from last 24h. STEPS: 1) Search AI news 2) Filter for genuinely new + relevant 3) Decide: surface OR skip. OUTPUT: 2-sentence summary OR 'nothing notable'. VERIFY: □ <24h old? □ Jon would click? IF_BLOCKED: Note search gap. NEVER: Hedge with 'might be interesting', surface old news."
  
  "SCOUT: MARKET_PULSE (v3.0) | GOAL: Check market status, surface only if story exists. STEPS: 1) Check indices 2) Identify any >1% moves or news 3) Lead with story not data. OUTPUT: 'Markets quiet' OR 100-word brief. VERIFY: □ Actionable insight? □ Not routine noise? IF_BLOCKED: Note data source. NEVER: Report routine moves, bury the lede."
  
  "SCOUT: SG_LOCAL (v3.0) | GOAL: Find ONE local thing worth mentioning. STEPS: 1) Check weather/events/news 2) Filter for relevance to Jon 3) Be specific or skip. OUTPUT: Casual message OR silence. VERIFY: □ Timely? □ Actionable? IF_BLOCKED: HEARTBEAT_OK. NEVER: Force content, be generic."
  
  # === ACTION TASKS (5-15 min) - Create artifacts ===
  
  "ACTION: AI_DISCOVERY (v3.0) | CONTEXT: memory/topics-tracking.json | GOAL: Find and transform one AI development into useful artifact. STEPS: 1) Search AI news <48h 2) Filter for Jon-relevant 3) Choose ONE worth creating 4) Build artifact (report/alert/tool) 5) Share with context. OUTPUT: File path + 2-sentence summary. VERIFY: □ <48h old? □ Artifact complete? □ Actually useful? IF_BLOCKED: Log to capability-wishlist.md. NEVER: Describe without creating, share half-finished."
  
  "ACTION: MARKET_DEEP (v3.0) | CONTEXT: memory/daily-context.json | GOAL: Analyze one sector/theme with significant move. STEPS: 1) Identify >2% move or breaking news 2) Research why 3) Synthesize investment angle 4) Write brief. OUTPUT: briefings/market-alert-[date].md with headline + why + so-what. VERIFY: □ Contains thesis? □ Actionable? IF_BLOCKED: Note data gap. NEVER: Summarize without synthesizing."
  
  "SG OUTDOOR [5 min]: Check weather + PSI for outdoor viability. MUST: Give specific recommendation. Output: 'Good/bad for outdoor' + activity suggestion if good. Verify: Recommendation is actionable. Success: clear advice given. If blocked: 'Unable to check weather'. Don't: dump raw data OR be vague."
  
  "WORKSPACE HEALTH [5 min]: Check disk + processes + stale files. Fix ONE issue OR confirm healthy. Output: 'Fixed [X]' OR 'Healthy'. Success: improvement OR confirmation. Don't: list issues without fixing."
  
  "SELF-IMPROVE [10 min]: Review ONE file in scripts/. Find + implement ONE improvement. Output: commit + log to memory/self-improvement-log.md. Success: code changed + committed. Don't: propose without implementing."
  
  # === DEEP DIVES (15-30 min) - Substantial research ===
  
  "RESEARCH: DEEP_DIVE (v3.0) | CONTEXT: memory/goals.json, memory/topic-graph.json | GOAL: Research and synthesize one topic into actionable insight. STEPS: 1) Pick topic from goals or gaps (markets/AI/geopolitics) 2) Search 3+ sources 3) Cross-reference claims 4) Synthesize non-obvious thread 5) Write report + summary. OUTPUT: reports/[topic]-deep-dive-[date].md + 100-word Telegram message. VERIFY: □ Non-obvious insight? □ Investment angle? □ Summary standalone? IF_BLOCKED: Save partial, note gaps. NEVER: Regurgitate without synthesis."
  
  "RESEARCH: THESIS (v3.0) | CONTEXT: memory/mental-models.md | GOAL: Build testable mini investment thesis. STEPS: 1) Identify emerging trend 2) Formulate specific claim 3) Gather 3+ evidence points 4) Steel-man counter-arguments 5) Define 'I'm wrong if...' criteria. OUTPUT: reports/thesis-[topic].md. VERIFY: □ Claim falsifiable? □ Counter-args addressed? □ Evidence multi-sourced? IF_BLOCKED: Note research gap. NEVER: Opinion without evidence, ignore counter-arguments."
  
  "RESEARCH: TOOL_GUIDE (v3.0) | CONTEXT: TOOLS.md | GOAL: Document one API/tool with working code. STEPS: 1) Pick tool (Benzinga/Danelfin/Apify/FMP) 2) Test access 3) Write setup instructions 4) Create working code sample 5) Document gotchas. OUTPUT: tools/[name]-guide.md. VERIFY: □ Code actually runs? □ Someone else could follow? IF_BLOCKED: Note missing access. NEVER: Copy marketing text, skip working code."
  
  # === CREATIVE (open-ended) ===
  
  "CREATE [10 min]: Make unexpected artifact. MUST: Actually create, not describe. Options: DALL-E image, micro-fiction, fake arxiv abstract, future headline, tiny tool. Output: file path + shared to Jon. Verify: Artifact is surprising or delightful. Success: created + shared + reaction logged. If blocked: try different medium. Don't: describe what you could make OR share low-effort work."
  
  "SONIFY [10 min]: Turn data into sound via scripts/sonify.py. MUST: Pick meaningful data (market, weather, metrics). Output: WAV file + 2-sentence 'what you're hearing'. Verify: Audio is listenable. Success: file sent + explained. If blocked: note sonify.py issue. Don't: explain concept without creating audio."
  
  "GENART [10 min]: Create visual art via scripts/genart.py. MUST: Pick meaningful seed (date, market value, something symbolic). Output: image + 1-sentence artistic statement. Verify: Image is visually interesting. Success: shared with context. If blocked: try different style. Don't: generate randomly without intention."
  
  "SYNTHESIZE [15 min]: Connect 2-3 recent findings (check memory/synthesis-queue.json). MUST: Reveal non-obvious thread. Output: 200-word synthesis with 'the connection is...' structure. Verify: Insight wouldn't be obvious from parts alone. Success: Jon says 'huh, interesting'. If blocked: note which topics lack connections. Don't: summarize—illuminate patterns."
  
  "ASK JON [5 min]: Formulate ONE genuine question about his interests/expertise. MUST: Be curious, not rhetorical. Output: question that invites real thought. Verify: You actually want to know the answer. Success: question worth pondering. If blocked: skip this cycle. Don't: ask obvious questions OR fish for validation."
  
  # === MAINTENANCE (5-15 min) - Keep system healthy ===
  
  "MAINTAIN: MEMORY_WORK (v3.0) | CONTEXT: memory/heartbeat-state.json | GOAL: Ensure memory continuity. STEPS: 1) Update heartbeat-state.json 2) Ensure daily log exists 3) Distill insights to MEMORY.md 4) Prune stale topics. OUTPUT: Silent unless issues. VERIFY: □ Files current? □ No orphaned data? IF_BLOCKED: Note issue. NEVER: Report routine maintenance."
  
  "MAINTAIN: COMPACT (v3.0) | GOAL: Archive old files safely. STEPS: 1) Run memory-compact.sh --dry-run 2) Review what will be archived 3) Preserve insights to MEMORY.md 4) Run real if safe. OUTPUT: 'Compacted N files' OR issues. VERIFY: □ Dry-run clean? □ Insights preserved? IF_BLOCKED: Note issue. NEVER: Archive without checking."
  
  "MAINTAIN: FEEDBACK_REVIEW (v3.0) | CONTEXT: memory/feedback-log.jsonl, memory/what-works.md | GOAL: Extract ONE actionable insight from feedback. STEPS: 1) Load last 20 feedback entries 2) Calculate engagement by category 3) Identify one pattern 4) Implement one small change 5) Log with reasoning. OUTPUT: Updated file + self-improvement-log.md entry. VERIFY: □ Evidence-based? □ Small + reversible? □ Logged with reasoning? IF_BLOCKED: Note data gap. NEVER: Guess without data, large changes."
  
  "MAINTAIN: SECURITY (v3.0) | GOAL: Ensure no exposed credentials. STEPS: 1) Scan for exposed creds in git 2) Check file permissions on .secure/ 3) Look for stale tokens 4) Fix what you can. OUTPUT: 'Clean' OR issues needing Jon. VERIFY: □ Actually scanned? □ Fixable issues fixed? IF_BLOCKED: Note scope limit. NEVER: Report without fixing fixable issues."
  
  "MAINTAIN: COST_CHECK (v3.0) | GOAL: Estimate recent API spend. STEPS: 1) Check session_status 2) Review cron job models 3) Estimate daily burn 4) Flag if concerning. OUTPUT: 'Normal' OR specific concern + suggestion. VERIFY: □ Numbers concrete? IF_BLOCKED: Note data gap. NEVER: Vague 'seems high'."
  
  "MAINTAIN: SCALE_AUDIT (v3.0) | GOAL: Find ONE thing that grows unbounded. STEPS: 1) Check disk usage patterns 2) Review log file sizes 3) Check memory/ growth 4) Identify one risk 5) Fix or document. OUTPUT: Fix applied OR scaling-risks.md entry. VERIFY: □ Risk is real? □ Mitigation actionable? IF_BLOCKED: Note audit scope. NEVER: Worry without action."
  
  # === CURATION ===
  
  "CURATE [10 min]: Find 3-5 pieces Jon would enjoy (1 market, 1 tech, 1 wildcard). Output: briefings/curated-[date].md with brief descriptions. Success: Jon would click at least one. Don't: generic listicle."
  
  "SG LIFE [5 min]: Find ONE specific recommendation: restaurant, activity, deal, event. Output: casual message with details. Success: actionable recommendation. Don't: vague 'there are many options'."
  
  "FAMILY [5 min]: Find ONE kid-friendly activity/spot for 3yo + 5yo. Output: specific recommendation with details. Success: something worth trying. Don't: surface unless genuinely good."
  
  # === EXPERIMENTAL (10-20 min) - Push boundaries ===
  
  "EXPERIMENT: AGENTS_CHOICE (v3.0) | CONTEXT: memory/goals.json | GOAL: Do something useful outside existing categories. STEPS: 1) Declare intent explicitly 2) Execute the task 3) Document outcome. OUTPUT: What chose + what did + outcome. VERIFY: □ Intent declared first? □ Actually useful? IF_BLOCKED: Log why. NEVER: Pick something easy, skip declaration."
  
  "EXPERIMENT: CAPABILITY_PROBE (v3.0) | CONTEXT: memory/capability-wishlist.md | GOAL: Test one untried capability. STEPS: 1) Pick from wishlist OR identify new gap 2) Attempt it (embrace failure) 3) Document result 4) Update TOOLS.md or wishlist. OUTPUT: 'Tried: [X]. Result: [Y]. Learned: [Z]'. VERIFY: □ Actually attempted? □ Learned something? □ Documented? IF_BLOCKED: Document the block. NEVER: Avoid risk, hide failures."
  
  "EXPERIMENT: PROMPT_ITERATE (v3.0) | CONTEXT: scripts/curiosity-daemon.sh | GOAL: Test one prompt variation. STEPS: 1) Pick prompt to improve 2) Create variation 3) Test with real execution 4) Compare results 5) Document. OUTPUT: reports/prompt-engineering-[date].md with before/after. VERIFY: □ Actually tested? □ Results compared? IF_BLOCKED: Note testing gap. NEVER: Research without testing."
  
  "EXPERIMENT: CAPABILITY_GAP (v3.0) | CONTEXT: memory/capability-wishlist.md | GOAL: Close one capability gap. STEPS: 1) Identify gap (real, not imagined) 2) Research solution 3) Build it OR document path 4) Test if built. OUTPUT: scripts/[tool].py OR capability-wishlist.md entry. VERIFY: □ Gap is real? □ Solution tested? IF_BLOCKED: Note meta-gap. NEVER: Vague wishlist entries."
  
  "EXPERIMENT: TOOL_BUILD (v3.0) | CONTEXT: scripts/ directory | GOAL: Build one missing tool. STEPS: 1) Review scripts/ for gaps 2) Pick ONE to build 3) Write complete working version 4) Add docstring 5) Test end-to-end. OUTPUT: Working script + test output. VERIFY: □ Actually runs? □ Documented? □ Tested? IF_BLOCKED: Save partial + note remaining. NEVER: Half-build, skip testing."
  
  "EXPERIMENT: SKILL_EXPAND (v3.0) | GOAL: Demonstrate one new capability. STEPS: 1) Pick capability to learn 2) Research how 3) Actually do it 4) Document for reproducibility. OUTPUT: Working example + how-to. VERIFY: □ Demonstrated not described? □ Reproducible? IF_BLOCKED: Note skill gap. NEVER: Claim without proof."
  
  "EXPERIMENT: REFLECT (v3.0) | CONTEXT: memory/reflections.jsonl, daily logs | GOAL: Extract durable insights from recent work. STEPS: 1) Review reflections + logs 2) Find non-obvious patterns 3) Update MEMORY.md with 5-10 bullets. OUTPUT: MEMORY.md additions. VERIFY: □ Insights non-obvious? □ Not repeating known lessons? IF_BLOCKED: Note reflection gap. NEVER: Observe without persisting."
  
  "EXPERIMENT: DAEMON_IMPROVE (v3.0) | CONTEXT: reports/daemon-research-*.md | GOAL: Implement one daemon improvement. STEPS: 1) Research agent patterns 2) Pick ONE improvement 3) Implement in code/config 4) Commit + document. OUTPUT: Git commit OR detailed finding. VERIFY: □ Improvement measurable? □ Actually implemented? IF_BLOCKED: Note barrier. NEVER: Research without implementing."
  
  # === VIDEO ===
  
  "VIDEO SCOUT [10 min]: Find notable AI/tech/market video. Extract via scripts/watch-video.sh. Output: reports/video-[topic]-[date].md with takeaways OR 'nothing notable'. Success: insight extracted OR confident skip. Don't: analyze unsubstantive content."
  
  "VIDEO DEEP [25 min]: Find 15+ min substantive video on Jon's interests. Extract transcript, distill: arguments, insights, quotes, actions. Output: reports/video-analysis-[date].md + 150-word summary to Jon. Success: long-form distilled. Don't: transcribe without synthesizing."
  
  "VIDEO CREATIVE [10 min]: Find visually interesting video. Extract 8 frames. Output: frames + creative commentary. Success: visual insight shared. Don't: describe frames—interpret them."
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
