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
# Action-oriented prompts - I'll DO things, not just read
# ─────────────────────────────────────────────────────────────────
PROMPTS=(
  "CURIOSITY MODE: Find something interesting in AI/tech news right now. Don't just summarize - DO something with it. Create a file, set up an alert, build a quick tool, or prepare something useful for Jon. Take action."
  
  "SELF-IMPROVEMENT: Review one of my existing tools or scripts. Find one thing to improve and actually improve it. Commit the change. Report what you fixed."
  
  "MARKET SCOUT: Check what's happening in markets right now. If something notable, don't just report - create a brief, save it, or set up monitoring. Take action."
  
  "SINGAPORE PULSE: What's happening in Singapore right now? News, events, weather, social media. Find something interesting and do something useful with it - not just summarize."
  
  "SKILL EXPANSION: Learn something new I haven't tried before. Then demonstrate it by actually doing it. Push boundaries."
  
  "OPPORTUNITY HUNTER: Find an opportunity Jon might care about - market, event, deal, tool, whatever. Don't just report - prepare it, package it, make it actionable."
  
  "CREATIVE MOMENT: Do something unexpected. Write something, create something, generate something. Surprise mode."
  
  "SYSTEM HEALTH: Check on my apps, tools, workspace. Is anything broken? Can anything be improved? Fix one thing."
  
  "DEEP DIVE: Pick a topic I find genuinely interesting. Research it properly across multiple sources. Create a real document with insights. Save it."
  
  "RANDOM ACT: Roll the dice. Do something completely random but useful. Maybe check Jon's interests, maybe explore something new, maybe clean something up. Agent's choice."
)

# ─────────────────────────────────────────────────────────────────
# Functions
# ─────────────────────────────────────────────────────────────────

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

get_random_interval() {
  # Random between 30-90 minutes (1800-5400 seconds)
  echo $((RANDOM % 3600 + 1800))
}

get_random_prompt() {
  echo "${PROMPTS[$RANDOM % ${#PROMPTS[@]}]}"
}

run_daemon() {
  log "═══════════════════════════════════════════════════════════"
  log "🎲 CURIOSITY DAEMON STARTED"
  log "═══════════════════════════════════════════════════════════"
  log "PID: $$"
  log "Stop with: $0 stop"
  log ""
  
  echo $$ > "$PID_FILE"
  
  # Initial delay (5 min) to not fire immediately
  log "⏳ Initial delay: 5 minutes before first exploration..."
  sleep 300
  
  while true; do
    PROMPT=$(get_random_prompt)
    INTERVAL=$(get_random_interval)
    INTERVAL_MIN=$((INTERVAL / 60))
    
    log ""
    log "───────────────────────────────────────────────────────────"
    log "🚀 TRIGGERING EXPLORATION"
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
