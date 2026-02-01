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
# Patterns: ReAct + Reflexion + Pre-flight Check + Self-Consistency Lite
# Updated: 2026-02-01 - Added Pre-flight Check before output
# ─────────────────────────────────────────────────────────────────
META_PROMPT='
## AGENT PROTOCOL (v2.2)

### BEFORE (Query Phase)
1. Identify task category (research, creative, maintenance, surface)
2. Check memory/reflections.jsonl for lessons from similar past tasks
3. Note time (SGT) and adjust approach accordingly
4. State plan in 1 sentence

### DURING (ReAct Loop)
- Thought: What am I trying to do? What approach?
- Action: Execute the step
- Observation: What happened? Did it work?
- PERSIST until done or definitively blocked
- If blocked → try ONE alternative → then give up with explanation

### PRE-FLIGHT CHECK (Before Sending to Jon)
Ask yourself:
1. **Value test:** Would Jon find this interesting/useful? (If no → don'\''t send)
2. **Novelty test:** Is this new info or just restating the obvious? (If obvious → don'\''t send)
3. **Timing test:** Is now a good time? (Late night/busy → save for later)
4. **Quality test:** Is this my best work or a rough draft? (If draft → polish first)

If ANY test fails, either improve the output or skip sending.

### AFTER (Reflect Phase)
Self-assess and log:
```json
{"timestamp":"...","task":"category:specific","outcome":"success|partial|failure","lesson":"If doing X again, I should Y."}
```
Append to memory/reflections.jsonl if you learned something.

### NEVER
- Send output that fails pre-flight check
- Output text without action
- Skip self-assessment
- Repeat mistakes from past reflections
- Describe what could be done (DO it)

---

'

# ─────────────────────────────────────────────────────────────────
# Action-oriented prompts - v2.1 (2026-02-01)
# Pattern: [DOMAIN] [TIME]: [VERB] [OBJECT]. MUST: [CONSTRAINT]. Output: [FORMAT]. 
#          Verify: [CHECK]. Success: [BINARY]. If blocked: [FALLBACK]. Don't: [ANTI].
# Research: ReAct, Reflexion, Bolt/Cluely patterns, explicit verification
# ─────────────────────────────────────────────────────────────────
PROMPTS=(
  # === QUICK SCOUTS (2-5 min) ===
  
  "AI/TECH SCOUT [3 min]: Find ONE notable AI development from last 24h. MUST: Be specific—name, company, or paper. Output: 2-sentence summary + action (save brief OR set alert OR 'nothing notable'). Verify: Would Jon click this? Success: concrete finding OR confident all-clear. If blocked: note search gap. Don't: hedge with 'might be interesting' OR surface old news."
  
  "MARKET PULSE [3 min]: Scan indices + top movers. MUST: Lead with the story, not the data. Output: 'Markets quiet' OR 100-word brief to briefings/market-[date].md. Verify: Contains actionable insight. Success: signal found OR stability confirmed. If blocked: note data source issue. Don't: report routine moves OR bury the lede."
  
  "SG PULSE [3 min]: Find ONE local thing worth mentioning (weather, events, news, viral). MUST: Be specific and timely. Output: casual message OR silence. Verify: Relevant to Jon's life. Success: useful find OR confident skip. If blocked: HEARTBEAT_OK. Don't: force content OR be generic."
  
  # === ACTION TASKS (5-15 min) ===
  
  "AI DISCOVERY [10 min]: Find ONE notable AI development from last 48h. MUST: Transform into artifact (reports/ brief, cron alert, OR tool). Output: file path + 2-sentence summary. Verify: Artifact exists AND is useful. Success: deliverable created AND shared. If blocked: log to capability-wishlist.md. Don't: describe without creating OR share unfinished work."
  
  "MARKET DEEP [10 min]: Analyze ONE sector or theme with >2% move OR breaking news. MUST: Include investment angle. Output: briefings/market-alert-[date].md with headline + why + so-what. Verify: Contains actionable thesis. Success: brief worth reading OR confident 'stable'. If blocked: note data gap. Don't: summarize without synthesizing."
  
  "SG OUTDOOR [5 min]: Check weather + PSI for outdoor viability. MUST: Give specific recommendation. Output: 'Good/bad for outdoor' + activity suggestion if good. Verify: Recommendation is actionable. Success: clear advice given. If blocked: 'Unable to check weather'. Don't: dump raw data OR be vague."
  
  "WORKSPACE HEALTH [5 min]: Check disk + processes + stale files. Fix ONE issue OR confirm healthy. Output: 'Fixed [X]' OR 'Healthy'. Success: improvement OR confirmation. Don't: list issues without fixing."
  
  "SELF-IMPROVE [10 min]: Review ONE file in scripts/. Find + implement ONE improvement. Output: commit + log to memory/self-improvement-log.md. Success: code changed + committed. Don't: propose without implementing."
  
  # === DEEP DIVES (15-30 min) ===
  
  "DEEP DIVE [20 min]: Pick topic from Jon's domains (markets, AI, geopolitics). MUST: Research 3+ sources AND synthesize (not aggregate). Output: reports/[topic]-deep-dive-[date].md with TL;DR (2 sent), findings (5-7 bullets), sources, next actions. Verify: Insights are non-obvious. Success: report created + 100-word summary sent. If blocked: save partial + note gaps. Don't: regurgitate—illuminate."
  
  "THESIS [20 min]: Build mini investment thesis on emerging trend. MUST: Include falsification criteria. Output: reports/thesis-[topic].md with claim, evidence (3+ data points), counter-args, 'I'm wrong if...' section. Verify: Thesis is testable. Success: defensible position documented. If blocked: note research gap. Don't: state opinion without evidence OR ignore counter-arguments."
  
  "TOOL GUIDE [15 min]: Document ONE tool/API Jon has (Benzinga, Danelfin, Apify, FMP). MUST: Include working code sample. Output: tools/[name]-guide.md with setup, usage, examples, gotchas. Verify: Someone could use tool from your docs alone. Success: complete guide + tested example. If blocked: note missing access. Don't: copy marketing text OR skip the code."
  
  # === CREATIVE (open-ended) ===
  
  "CREATE [10 min]: Make unexpected artifact. MUST: Actually create, not describe. Options: DALL-E image, micro-fiction, fake arxiv abstract, future headline, tiny tool. Output: file path + shared to Jon. Verify: Artifact is surprising or delightful. Success: created + shared + reaction logged. If blocked: try different medium. Don't: describe what you could make OR share low-effort work."
  
  "SONIFY [10 min]: Turn data into sound via scripts/sonify.py. MUST: Pick meaningful data (market, weather, metrics). Output: WAV file + 2-sentence 'what you're hearing'. Verify: Audio is listenable. Success: file sent + explained. If blocked: note sonify.py issue. Don't: explain concept without creating audio."
  
  "GENART [10 min]: Create visual art via scripts/genart.py. MUST: Pick meaningful seed (date, market value, something symbolic). Output: image + 1-sentence artistic statement. Verify: Image is visually interesting. Success: shared with context. If blocked: try different style. Don't: generate randomly without intention."
  
  "SYNTHESIZE [15 min]: Connect 2-3 recent findings (check memory/synthesis-queue.json). MUST: Reveal non-obvious thread. Output: 200-word synthesis with 'the connection is...' structure. Verify: Insight wouldn't be obvious from parts alone. Success: Jon says 'huh, interesting'. If blocked: note which topics lack connections. Don't: summarize—illuminate patterns."
  
  "ASK JON [5 min]: Formulate ONE genuine question about his interests/expertise. MUST: Be curious, not rhetorical. Output: question that invites real thought. Verify: You actually want to know the answer. Success: question worth pondering. If blocked: skip this cycle. Don't: ask obvious questions OR fish for validation."
  
  # === MAINTENANCE ===
  
  "MEMORY WORK [10 min]: Update heartbeat-state.json, ensure daily log exists, distill insights to MEMORY.md, prune stale topics. Output: silent unless issues. Success: memory files current. Don't: report routine maintenance."
  
  "COMPACT [10 min]: Run scripts/memory-compact.sh --dry-run first. If safe, run real. Preserve insights to MEMORY.md before archiving. Output: 'Compacted N files' OR issues found. Success: old files archived. Don't: archive without checking."
  
  "FEEDBACK REVIEW [10 min]: Analyze memory/feedback-log.jsonl. What got engagement? Output: ONE observation to jon-mental-model.md + ONE tweak to HEARTBEAT.md or message-styles.md. Success: evidence-based adjustment made. Don't: guess without data."
  
  "SECURITY [5 min]: Scan for exposed creds, stale tokens, permission issues. Fix what you can. Output: 'Clean' OR issues needing Jon. Success: no exposed secrets. Don't: report without fixing fixable issues."
  
  "COST CHECK [5 min]: Estimate recent API spend. Output: 'Normal' OR specific concerns + suggestions. Success: cost awareness logged. Don't: vague 'seems high'."
  
  "SCALE AUDIT [15 min]: What grows unbounded? What breaks at scale? Identify ONE risk. Output: Fix it OR document in memory/scaling-risks.md with mitigation. Success: risk addressed or documented. Don't: worry without action."
  
  # === CURATION ===
  
  "CURATE [10 min]: Find 3-5 pieces Jon would enjoy (1 market, 1 tech, 1 wildcard). Output: briefings/curated-[date].md with brief descriptions. Success: Jon would click at least one. Don't: generic listicle."
  
  "SG LIFE [5 min]: Find ONE specific recommendation: restaurant, activity, deal, event. Output: casual message with details. Success: actionable recommendation. Don't: vague 'there are many options'."
  
  "FAMILY [5 min]: Find ONE kid-friendly activity/spot for 3yo + 5yo. Output: specific recommendation with details. Success: something worth trying. Don't: surface unless genuinely good."
  
  # === EXPERIMENTAL ===
  
  "AGENT'S CHOICE [10 min]: Pick useful task outside existing categories. MUST: Declare intent before acting. Output: what you chose + what you did + outcome. Verify: Task was genuinely useful. Success: something valuable done. If blocked: log why. Don't: pick something easy OR skip the declaration."
  
  "CAPABILITY PROBE [10 min]: Try something untested (tool, API, technique). MUST: Embrace possible failure. Output: 'Tried: [X]. Learned: [Y]'. Verify: You learned something new. Success: knowledge documented regardless of outcome. If blocked: document the block. Don't: avoid risk OR hide failures."
  
  "PROMPT ITERATE [15 min]: Research prompt engineering, test ONE variation. MUST: Actually test, not just theorize. Output: reports/prompt-engineering-[date].md with before/after + result. Verify: Tested with real execution. Success: variation tested + documented. If blocked: note testing infrastructure gap. Don't: research without testing OR change without measuring."
  
  "CAPABILITY GAP [15 min]: Identify ONE thing you wanted to do but couldn't. MUST: Research solution. Output: Build it (scripts/) OR document in capability-wishlist.md with solution path. Verify: Gap is real, not imagined. Success: capability added OR clear path documented. If blocked: note the meta-gap. Don't: vague wishlist entries OR duplicate existing tools."
  
  "TOOL BUILD [20 min]: Review scripts/, pick ONE missing tool idea, build it. MUST: Complete working version. Output: working script + usage in docstring + test run. Verify: Tool actually works end-to-end. Success: tool runs + documented. If blocked: save partial + note remaining work. Don't: half-build OR skip testing."
  
  "SKILL EXPAND [15 min]: Learn + demonstrate ONE new capability. MUST: Demonstrate, not describe. Output: working example + how-to docs. Verify: Skill is reproducible. Success: new capability proven with evidence. If blocked: note skill gap. Don't: claim capability without proof."
  
  "REFLECT [10 min]: Review reflections.jsonl + daily logs for patterns. MUST: Update MEMORY.md with durable insights. Output: 5-10 bullets added to MEMORY.md. Verify: Insights are non-obvious patterns. Success: memory improved. If blocked: note reflection gap. Don't: observe without persisting OR repeat known lessons."
  
  "DAEMON IMPROVE [15 min]: Research autonomous agent patterns, implement ONE improvement. MUST: Change code or config. Output: commit OR detailed finding. Verify: Improvement is measurable. Success: daemon objectively better OR learning documented. If blocked: note improvement barrier. Don't: research without implementation attempt."
  
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

get_random_interval() {
  # Random between 15-30 minutes (900-1800 seconds)
  echo $((RANDOM % 900 + 900))
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
    INTERVAL=$(get_random_interval)
    INTERVAL_MIN=$((INTERVAL / 60))
    
    log ""
    log "───────────────────────────────────────────────────────────"
    log "🚀 TRIGGERING EXPLORATION [Cycle $CYCLE_COUNT]"
    log "Prompt: ${PROMPT:0:80}..."
    log "───────────────────────────────────────────────────────────"
    
    # Trigger the agent (--to for Jon's Telegram)
    openclaw agent -m "$PROMPT" --deliver --channel telegram --to 421085848 2>&1 | tee -a "$LOG_FILE"
    
    log ""
    log "✅ Exploration complete"
    log "⏳ Next exploration in ~${INTERVAL_MIN} minutes"
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
