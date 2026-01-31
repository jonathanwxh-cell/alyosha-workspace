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
# Based on research: Reflexion, Critic/Judge, Persistence patterns
# ─────────────────────────────────────────────────────────────────
META_PROMPT='
## AGENT PROTOCOL

BEFORE STARTING:
1. Check memory/reflections.jsonl for lessons from similar past tasks
2. Note the current time (SGT) and adjust approach accordingly
3. Briefly outline your plan (1-2 sentences)

DURING EXECUTION:
- PERSISTENCE: Keep going until the task is complete
- If blocked, try alternative approaches before giving up
- Document what you tried if something fails

AFTER COMPLETING:
- Self-assess: Did you meet the success criteria?
- If you learned something, append to memory/reflections.jsonl
- Be honest about partial success or failure

DO NOT:
- Output walls of text without taking action
- Skip the self-assessment step
- Repeat mistakes from past reflections
- Give up without trying alternatives
- Just describe what could be done (DO it)

---

'

# ─────────────────────────────────────────────────────────────────
# Action-oriented prompts - Improved with explicit structure
# Pattern: [DOMAIN] [DEPTH]: [Task]. [Output]. [Success criteria]. [Anti-pattern].
# ─────────────────────────────────────────────────────────────────
PROMPTS=(
  # === QUICK SCOUTS (2-5 min, lightweight) ===
  
  "AI/TECH QUICK SCOUT: Spend 3 minutes scanning tech news. Find ONE thing worth knowing. If nothing notable today, reply 'Nothing notable in AI/tech.' If found: 2-3 sentence summary + one action (save brief, set alert, or flag for later). No fluff."
  
  "MARKET QUICK SCOUT: 3-minute market scan. Check major indices, any big movers, earnings surprises. If nothing unusual: 'Markets quiet.' If notable: Create 100-word brief, save to briefings/market-quick-[date].md. Include: what moved, why, watch item."
  
  "SINGAPORE QUICK SCOUT: Quick scan of SG news/social. Find ONE local thing worth mentioning. Weather alerts, viral stories, events. If nothing: stay silent. If found: casual message to Jon, no file needed."
  
  # === ACTION TASKS (5-15 min, concrete deliverables) ===
  
  "CURIOSITY ACTION: Find something genuinely interesting in AI/tech. Don't summarize — TRANSFORM it. Output options: create a brief (reports/), set up a cron monitor, build a quick tool, or draft something Jon could use. Success = tangible artifact created. Anti-pattern: walls of text with no action."
  
  "MARKET ACTION: Check markets NOW. If any sector moves >2% or major news breaks, create briefings/market-alert-[date].md with: Headline, What happened, Why it matters, Action items. If quiet: 'Markets stable, no alert needed.' Success = actionable brief or confident all-clear."
  
  "SG OUTDOOR GUIDE: Check weather + PSI + weekend events. Update Jon on whether it's a good day for outdoor activities with kids. Specific recommendations if conditions are good. Save to briefings/ if substantial."
  
  "WORKSPACE HEALTH: Scan workspace for issues. Check: disk space, running processes, stale files, broken tools. Fix ONE thing. Report: 'Fixed [X]' or 'Workspace healthy.' Success = something improved or confirmed working."
  
  "SELF-IMPROVE ACTION: Review one file in scripts/ or tools/. Find ONE concrete improvement. Implement it. Commit with clear message. Log to memory/self-improvement-log.md. Report: 'Improved [file] by [change].' Anti-pattern: just describing what could be done."
  
  # === DEEP DIVES (15-30 min, thorough research) ===
  
  "DEEP DIVE: Pick a topic that genuinely interests you from Jon's domains (markets, AI, geopolitics, science, longevity). Research across 3+ sources. Create reports/[topic]-deep-dive-[date].md with: TL;DR (2 sentences), Key findings (5-7 bullets), Sources, Open questions, Action items. Send 100-word summary to Jon."
  
  "THESIS BUILDER: Identify an emerging trend or contrarian take. Build a mini investment/research thesis. Include: the claim, supporting evidence, counter-arguments, what would prove it wrong. Save to reports/thesis-[topic].md. This is thinking, not just aggregating."
  
  "TOOL DEEP DIVE: Research one tool or API Jon has access to (Benzinga, Danelfin, Apify, etc). Document: what it does, how to use it, concrete use cases, integration ideas. Save to tools/[name]-guide.md. Bonus: build a working example."
  
  # === CREATIVE (open-ended, surprise factor) ===
  
  "CREATIVE MOMENT: Make something unexpected. Options: generate an image visualizing a concept, write micro-fiction, create an absurdist artifact (fake arxiv abstract, future news headline, product launch memo), prototype a tiny tool. Constraint: must be shareable, not just described. Save/send the artifact."
  
  "SONIFICATION: Turn something into sound using scripts/sonify.py. Options: recent market data, weather patterns, any numerical sequence. Create an audio piece that represents the data musically. Send the WAV file with a brief explanation of what it represents. Data → Sound → Insight."
  
  "GENERATIVE ART: Create algorithmic visual art using scripts/genart.py. Styles: flow (particle fields), fractal (mandelbrot), waves (interference patterns), circles (recursive geometry). Pick a style, generate with a meaningful seed (date, number from news, etc), share the image with a brief artistic statement. Code → Image → Beauty."
  
  "SYNTHESIS: Review memory/synthesis-queue.json and recent daily logs. Find a non-obvious connection between 2-3 things surfaced recently. Write a 200-word synthesis piece that reveals the thread. This is insight, not summary."
  
  "QUESTION: Ask Jon ONE genuinely curious question based on his interests or recent conversations. Not rhetorical, not sycophantic — something you actually want to know. Good questions > good answers."
  
  # === MAINTENANCE & META ===
  
  "MEMORY MAINTENANCE: Review memory/ files. Update heartbeat-state.json. Check if daily log exists, create if not. Distill any insights worth keeping to MEMORY.md. Prune stale items from topics-tracking.json. Silent unless issues found."
  
  "MEMORY COMPACTION: Run scripts/memory-compact.sh --dry-run first to preview. If reasonable, run without --dry-run. This archives old daily logs into weekly summaries, moves old reports/briefings to archive/, and trims tracking files. Before archiving, scan for any insights worth preserving to MEMORY.md. Report what was compacted."
  
  "FEEDBACK REVIEW: Check memory/feedback-log.jsonl and recent conversations. What got engagement? What was ignored? Update memory/jon-mental-model.md with one observation. Adjust one thing in HEARTBEAT.md or message-styles.md based on evidence."
  
  "SECURITY SCAN: Quick security hygiene check. Look for: exposed credentials in files, tokens needing rotation, permissions issues. Fix what you can. Report issues that need Jon's action. Success = cleaner security posture."
  
  "COST CHECK: Estimate recent API usage (searches, model calls). Are we being efficient? Any obvious waste? Report: 'API usage normal' or flag specific concerns with suggestions."
  
  "SUSTAINABILITY AUDIT: Project forward 6-12 months. What grows unbounded? (files, logs, memory, git history, cron jobs). What breaks at scale? What's inefficient now but tolerable, that won't be later? What assumptions won't hold? Identify ONE scaling risk and either fix it or document it in memory/scaling-risks.md with mitigation plan. This is how I avoid architectural debt."
  
  # === CURATION & LIFESTYLE ===
  
  "CONTENT CURATOR: Find 3-5 pieces of content Jon might genuinely enjoy. Mix: one market/finance, one tech/AI, one wildcard. Quality over quantity. Brief descriptions. Save to briefings/curated-[date].md. Anti-pattern: generic listicles."
  
  "SINGAPORE LIFE: Go beyond news. Find: a restaurant/cafe worth trying, a weekend activity, a local deal, or an event. Make it specific and practical. Casual message format, not a report."
  
  "FAMILY INTEL: Jon has 2 kids (3yo, 5yo). Find ONE kid-friendly activity, event, or spot in Singapore. Specific recommendation with details. Only surface if it's genuinely good."
  
  # === EXPERIMENTAL ===
  
  "RANDOM ACT: Agent's choice. Pick something useful that doesn't fit other categories. Could be: organizing files, exploring a new capability, checking on a project, or pure curiosity. Surprise yourself."
  
  "CAPABILITY PROBE: Try something you haven't done before or aren't sure works. Test a tool, explore an API, attempt a new output format. Report what you learned. Failure is acceptable — learning isn't optional."
  
  "PROMPT ENGINEERING: Research better ways to prompt myself. Find examples of effective action-oriented prompts. Test a variation. If improvement found, update this PROMPTS array in curiosity-daemon.sh."
  
  "CAPABILITY GAP: Reflect on recent tasks. What did I want to do but couldn't? What was clunky or manual that could be automated? What would make me more useful? Identify ONE gap. Then: research if a solution exists (API, tool, technique). If buildable, create it in scripts/ or tools/. If not, document the gap in memory/capability-wishlist.md. Success = new capability added OR gap clearly documented for future."
  
  "TOOL INVENTOR: Review scripts/ and think about what's missing. What would a truly useful agent have? Pick ONE idea and build it. Could be: a new data source, a workflow automation, a monitoring tool, an integration. Write the code, test it, document usage. Add to curiosity-daemon prompts if it enables new actions. This is how I evolve."
  
  "SKILL EXPANSION: Learn something new I haven't tried before. Research a capability, then DEMONSTRATE it by actually doing it. Don't just describe — build, create, or execute. Push boundaries. Success = new capability proven working + documented for future use."
  
  "REFLEXION: Review memory/reflections.jsonl and recent daily logs. What patterns emerge? What mistakes keep happening? What's working well? Write a brief synthesis (5-10 bullets) and update memory/jon-mental-model.md or MEMORY.md with durable insights. This is how I learn from experience."
  
  "DAEMON RESEARCH: Research how to make this curiosity daemon better. Look at autonomous agent patterns, prompt engineering techniques, scheduling strategies. Find ONE concrete improvement and implement it. Update the daemon code or document the finding."
  
  # === VIDEO ANALYSIS ===
  
  "VIDEO SCOUT: Search for a notable recent video in AI/tech/markets (conference talks, interviews, explainers). Use scripts/watch-video.sh to extract transcript or frames. Analyze content. Output: If insightful, create reports/video-[topic]-[date].md with key takeaways. If not worth it: 'No notable videos found.' Prefer talks/interviews over entertainment."
  
  "VIDEO DEEP DIVE: Find a substantive video (15+ min) on a topic Jon cares about. Run scripts/watch-video.sh to get transcript. Extract: key arguments, novel insights, quotable moments, action items. Create reports/video-analysis-[date].md. Send 150-word summary to Jon. Success = distilled value from long-form content."
  
  "VIDEO CREATIVE: Find a visually interesting or unusual video. Extract frames with scripts/watch-video.sh --frames 8. Analyze the visuals. Write a brief creative response — could be observations, connections, or inspired ideas. Share frames + commentary with Jon."
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
