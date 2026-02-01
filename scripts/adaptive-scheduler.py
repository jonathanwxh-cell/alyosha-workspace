#!/usr/bin/env python3
"""
adaptive-scheduler.py - Smart timing for autonomous agent actions (v2)

Outputs optimal interval (in seconds) based on:
- Time of day (SGT) with task-type awareness
- Engagement patterns (backoff + burst mode)
- Day of week
- Recent action count

v2 Changes (2026-02-02):
- Added backoff tracking (consecutive unreplied surfaces)
- Added burst mode detection (rapid engagement accelerates)
- Better integration with scheduling-intelligence.json
- Task-time matching hints

Usage:
  python3 adaptive-scheduler.py              # Get next interval
  python3 adaptive-scheduler.py --status     # Show current state
  python3 adaptive-scheduler.py --log-action # Log that an action was taken
  python3 adaptive-scheduler.py --log-reply  # Log that user replied (resets backoff)
  python3 adaptive-scheduler.py --task-hint  # Get optimal task type for now
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw" / "workspace"
SCHEDULE_FILE = WORKSPACE / "memory" / "scheduling-intelligence.json"
FEEDBACK_FILE = WORKSPACE / "memory" / "feedback-log.jsonl"
STATE_FILE = WORKSPACE / "memory" / "scheduler-state.json"

# Base intervals (seconds)
BASE_INTERVAL = 1800  # 30 minutes (default)
MIN_INTERVAL = 600    # 10 minutes (burst mode)
MAX_INTERVAL = 5400   # 90 minutes (heavy backoff)

# Backoff config
BACKOFF_THRESHOLD = 3        # Unreplied surfaces before backoff
BACKOFF_MULTIPLIER = 1.5     # Multiply interval by this per threshold
MAX_BACKOFF_LEVEL = 3        # Cap backoff at this level

# Burst mode config
BURST_WINDOW_MINUTES = 30    # Window to detect burst
BURST_THRESHOLD = 2          # Replies in window to trigger burst
BURST_MULTIPLIER = 0.5       # Faster intervals in burst mode

def get_sgt_now():
    """Get current datetime in Singapore Time."""
    sgt = timezone(timedelta(hours=8))
    return datetime.now(sgt)

def get_sgt_hour():
    """Get current hour in Singapore Time."""
    return get_sgt_now().hour

def get_day_of_week():
    """Get current day (0=Monday, 6=Sunday)."""
    return get_sgt_now().weekday()

def load_schedule_config():
    """Load scheduling intelligence config."""
    if SCHEDULE_FILE.exists():
        return json.loads(SCHEDULE_FILE.read_text())
    return {}

def load_scheduler_state():
    """Load scheduler state."""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {
        "lastActionTs": None,
        "actionsToday": 0,
        "lastDate": None,
        "unrepliedCount": 0,
        "backoffLevel": 0,
        "recentReplies": [],  # Timestamps of recent replies for burst detection
        "burstMode": False
    }

def save_scheduler_state(state):
    """Save scheduler state."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))

def load_recent_engagement():
    """Load recent engagement signals from feedback log."""
    if not FEEDBACK_FILE.exists():
        return []
    
    entries = []
    for line in FEEDBACK_FILE.read_text().strip().split('\n'):
        if line:
            try:
                entries.append(json.loads(line))
            except:
                pass
    
    # Last 24 hours of entries
    recent = []
    cutoff = datetime.now(timezone.utc).timestamp() - 86400
    for e in entries:
        ts = e.get('timestamp') or e.get('ts')
        if ts:
            try:
                entry_ts = datetime.fromisoformat(ts.replace('Z', '+00:00')).timestamp()
                if entry_ts > cutoff:
                    recent.append(e)
            except:
                pass
    return recent

def detect_burst_mode(state: dict) -> bool:
    """
    Detect if we're in burst mode (rapid engagement).
    Returns True if 2+ replies in last 30 minutes.
    """
    now = datetime.now(timezone.utc).timestamp()
    cutoff = now - (BURST_WINDOW_MINUTES * 60)
    
    recent_replies = state.get("recentReplies", [])
    # Filter to only recent
    recent = [ts for ts in recent_replies if ts > cutoff]
    
    # Update state with filtered list
    state["recentReplies"] = recent
    
    return len(recent) >= BURST_THRESHOLD

def calculate_time_multiplier(hour: int, config: dict) -> float:
    """
    Calculate interval multiplier based on time of day (SGT).
    Lower = shorter intervals (more active).
    
    Research-backed windows:
    - 6-8am: Early morning, high attention (Jon's observed fast-reply time)
    - 8-12pm: Peak working memory, good for complex content
    - 12-2pm: Post-lunch dip, lighter touch
    - 2-6pm: Second cognitive peak
    - 6-10pm: Good for synthesis, reflection
    - 10pm-6am: Sleep/autonomous work
    """
    # Get config windows
    adaptive = config.get("adaptiveRules", {}).get("proactiveSurface", {})
    avoid_hours = set(adaptive.get("avoidHours", [23, 0, 1, 2, 3, 4, 5, 6, 7]))
    
    # Sleep hours - longest intervals
    if hour in [23, 0, 1, 2, 3, 4, 5]:
        return 2.5  # Very long intervals during sleep
    
    # Early morning (6-8am) - Jon shows fast replies here
    if hour in [6, 7]:
        return 0.7  # Shorter intervals, he's attentive
    
    # Peak morning (8-11am) - highest engagement potential
    if hour in [8, 9, 10, 11]:
        return 0.8
    
    # Lunch dip (12-2pm) - ease off
    if hour in [12, 13]:
        return 1.3
    
    # Afternoon (2-6pm) - good, but variable
    if hour in [14, 15, 16, 17]:
        return 1.0
    
    # Evening (6-10pm) - good for reflection/synthesis
    if hour in [18, 19, 20, 21, 22]:
        return 0.9
    
    return 1.0

def calculate_backoff_multiplier(state: dict) -> float:
    """
    Calculate backoff multiplier based on unreplied surfaces.
    Increases interval when not getting engagement.
    """
    unreplied = state.get("unrepliedCount", 0)
    
    if unreplied < BACKOFF_THRESHOLD:
        return 1.0
    
    # Calculate backoff level (1, 2, or 3)
    level = min((unreplied - BACKOFF_THRESHOLD) // BACKOFF_THRESHOLD + 1, MAX_BACKOFF_LEVEL)
    state["backoffLevel"] = level
    
    return BACKOFF_MULTIPLIER ** level

def calculate_burst_multiplier(state: dict) -> float:
    """
    Calculate burst mode multiplier.
    When Jon is actively engaged, speed up.
    """
    if detect_burst_mode(state):
        state["burstMode"] = True
        return BURST_MULTIPLIER
    else:
        state["burstMode"] = False
        return 1.0

def calculate_day_multiplier(day: int, config: dict) -> float:
    """
    Day of week adjustment based on config.
    """
    adaptive = config.get("adaptiveScheduling", {}).get("dayOfWeek", {})
    
    # Weekend (Sat=5, Sun=6)
    if day >= 5:
        return adaptive.get("weekend", {}).get("surfaceWeight", 0.7)
    
    return adaptive.get("weekday", {}).get("surfaceWeight", 1.0)

def calculate_actions_multiplier(state: dict) -> float:
    """
    Slow down if many actions already today.
    """
    today = get_sgt_now().strftime("%Y-%m-%d")
    if state.get("lastDate") != today:
        return 1.0
    
    actions = state.get("actionsToday", 0)
    if actions >= 10:
        return 1.8
    elif actions >= 7:
        return 1.5
    elif actions >= 5:
        return 1.2
    return 1.0

def get_optimal_interval() -> int:
    """Calculate optimal interval for next action."""
    config = load_schedule_config()
    state = load_scheduler_state()
    hour = get_sgt_hour()
    day = get_day_of_week()
    
    # Calculate multipliers
    time_mult = calculate_time_multiplier(hour, config)
    backoff_mult = calculate_backoff_multiplier(state)
    burst_mult = calculate_burst_multiplier(state)
    day_mult = calculate_day_multiplier(day, config)
    actions_mult = calculate_actions_multiplier(state)
    
    # Combined multiplier (burst overrides backoff)
    if state.get("burstMode"):
        # In burst mode, ignore backoff
        total_mult = time_mult * burst_mult * day_mult
    else:
        total_mult = time_mult * backoff_mult * day_mult * actions_mult
    
    # Calculate interval
    interval = int(BASE_INTERVAL * total_mult)
    
    # Clamp to bounds
    interval = max(MIN_INTERVAL, min(MAX_INTERVAL, interval))
    
    # Save updated state
    save_scheduler_state(state)
    
    return interval

def get_task_hint() -> str:
    """
    Get optimal task type for current time.
    Returns category hint based on time of day.
    """
    hour = get_sgt_hour()
    
    if hour in [6, 7]:
        return "scout,quick"  # Quick checks, high attention
    elif hour in [8, 9, 10, 11]:
        return "research,deep"  # Complex analytical work
    elif hour in [12, 13]:
        return "maintain,light"  # Light work during lunch
    elif hour in [14, 15, 16, 17]:
        return "action,create"  # Afternoon creativity
    elif hour in [18, 19, 20, 21, 22]:
        return "synthesize,curate"  # Evening reflection
    elif hour in [23, 0, 1, 2, 3, 4, 5]:
        return "autonomous,build"  # Night = background work
    
    return "any"

def log_action():
    """Log that an action was taken (surface sent)."""
    state = load_scheduler_state()
    today = get_sgt_now().strftime("%Y-%m-%d")
    
    # Reset daily counter if new day
    if state.get("lastDate") != today:
        state["actionsToday"] = 1
        state["lastDate"] = today
    else:
        state["actionsToday"] = state.get("actionsToday", 0) + 1
    
    state["lastActionTs"] = datetime.now(timezone.utc).isoformat()
    
    # Increment unreplied counter
    state["unrepliedCount"] = state.get("unrepliedCount", 0) + 1
    
    save_scheduler_state(state)
    print(f"Logged action #{state['actionsToday']} (unreplied: {state['unrepliedCount']})")

def log_reply():
    """Log that user replied (resets backoff, adds to burst detection)."""
    state = load_scheduler_state()
    now = datetime.now(timezone.utc).timestamp()
    
    # Reset unreplied counter
    state["unrepliedCount"] = 0
    state["backoffLevel"] = 0
    
    # Add to recent replies for burst detection
    recent_replies = state.get("recentReplies", [])
    recent_replies.append(now)
    
    # Keep only last hour of replies
    cutoff = now - 3600
    state["recentReplies"] = [ts for ts in recent_replies if ts > cutoff]
    
    save_scheduler_state(state)
    
    burst = detect_burst_mode(state)
    print(f"Logged reply. Backoff reset. Burst mode: {burst}")

def show_status():
    """Show current scheduling status."""
    config = load_schedule_config()
    state = load_scheduler_state()
    hour = get_sgt_hour()
    day = get_day_of_week()
    
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    sgt_now = get_sgt_now()
    
    print("=" * 50)
    print("ADAPTIVE SCHEDULER STATUS (v2)")
    print("=" * 50)
    print(f"Current time: {sgt_now.strftime('%H:%M')} SGT ({days[day]})")
    print()
    
    # Load and calculate multipliers
    time_mult = calculate_time_multiplier(hour, config)
    backoff_mult = calculate_backoff_multiplier(state)
    burst_mult = calculate_burst_multiplier(state)
    day_mult = calculate_day_multiplier(day, config)
    actions_mult = calculate_actions_multiplier(state)
    
    print("Multipliers:")
    print(f"  Time of day:   {time_mult:.2f} {'⚡ peak' if time_mult < 0.9 else '😴 slow' if time_mult > 1.2 else ''}")
    print(f"  Backoff:       {backoff_mult:.2f} (unreplied: {state.get('unrepliedCount', 0)})")
    print(f"  Burst mode:    {burst_mult:.2f} {'🔥 ACTIVE' if state.get('burstMode') else ''}")
    print(f"  Day of week:   {day_mult:.2f} {'(weekend)' if day >= 5 else ''}")
    print(f"  Actions today: {actions_mult:.2f} ({state.get('actionsToday', 0)} actions)")
    print()
    
    interval = get_optimal_interval()
    print(f"Optimal interval: {interval}s ({interval//60}m {interval%60}s)")
    print(f"Range: {MIN_INTERVAL//60}m - {MAX_INTERVAL//60}m")
    print()
    
    hint = get_task_hint()
    print(f"Task hint for now: {hint}")
    print()
    
    print("State:")
    print(f"  Last action: {state.get('lastActionTs', 'never')}")
    print(f"  Backoff level: {state.get('backoffLevel', 0)}/{MAX_BACKOFF_LEVEL}")
    print(f"  Recent replies: {len(state.get('recentReplies', []))} in last hour")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "--status":
            show_status()
        elif arg == "--log-action":
            log_action()
        elif arg == "--log-reply":
            log_reply()
        elif arg == "--task-hint":
            print(get_task_hint())
        else:
            print(__doc__)
    else:
        # Default: output optimal interval
        print(get_optimal_interval())
