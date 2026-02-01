#!/usr/bin/env python3
"""
adaptive-scheduler.py - Smart timing for autonomous agent actions

Outputs optimal interval (in seconds) based on:
- Time of day (SGT)
- Day of week
- Recent engagement patterns
- Time since last action

Usage:
  python3 adaptive-scheduler.py              # Get next interval
  python3 adaptive-scheduler.py --status     # Show current state
  python3 adaptive-scheduler.py --log-action # Log that an action was taken
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw" / "workspace"
SCHEDULE_FILE = WORKSPACE / "memory" / "scheduling-intelligence.json"
FEEDBACK_FILE = WORKSPACE / "memory" / "feedback-log.jsonl"
STATE_FILE = WORKSPACE / "memory" / "scheduler-state.json"

# Base intervals (seconds)
BASE_INTERVAL = 1200  # 20 minutes
MIN_INTERVAL = 600    # 10 minutes (high engagement)
MAX_INTERVAL = 3600   # 60 minutes (low engagement / quiet hours)

def get_sgt_hour():
    """Get current hour in Singapore Time."""
    from datetime import timezone, timedelta
    sgt = timezone(timedelta(hours=8))
    return datetime.now(sgt).hour

def get_day_of_week():
    """Get current day (0=Monday, 6=Sunday)."""
    from datetime import timezone, timedelta
    sgt = timezone(timedelta(hours=8))
    return datetime.now(sgt).weekday()

def load_schedule_config():
    """Load scheduling intelligence config."""
    if SCHEDULE_FILE.exists():
        return json.loads(SCHEDULE_FILE.read_text())
    return {}

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

def load_scheduler_state():
    """Load scheduler state (last action time, etc)."""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"lastActionTs": None, "actionsToday": 0, "lastDate": None}

def save_scheduler_state(state):
    """Save scheduler state."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))

def calculate_time_multiplier(hour: int, config: dict) -> float:
    """
    Calculate interval multiplier based on time of day.
    Lower = shorter intervals (more active), Higher = longer intervals.
    """
    windows = config.get("engagementWindows", {})
    
    # Peak hours (night owl: 22-07) - most active
    peak = windows.get("peak", {})
    peak_start = peak.get("start", 22)
    peak_end = peak.get("end", 7)
    
    if peak_start > peak_end:  # Crosses midnight
        if hour >= peak_start or hour < peak_end:
            return 0.7  # 30% shorter intervals
    else:
        if peak_start <= hour < peak_end:
            return 0.7
    
    # Low engagement (morning with kids: 8-12)
    low = windows.get("low", {})
    low_start = low.get("start", 8)
    low_end = low.get("end", 12)
    if low_start <= hour < low_end:
        return 1.8  # 80% longer intervals
    
    # Avoid hours (lunch: 12-14)
    avoid = windows.get("avoid", {})
    for rng in avoid.get("ranges", [[12, 14]]):
        if rng[0] <= hour < rng[1]:
            return 2.0  # Double intervals
    
    # Default (good/neutral hours)
    return 1.0

def calculate_engagement_multiplier(recent_engagement: list) -> float:
    """
    Calculate multiplier based on recent engagement.
    High engagement = shorter intervals, no engagement = longer.
    """
    if not recent_engagement:
        return 1.2  # Slightly longer if no data
    
    # Count positive signals in last 6 hours
    positive = 0
    negative = 0
    
    cutoff = datetime.now(timezone.utc).timestamp() - 21600  # 6 hours
    for e in recent_engagement:
        ts = e.get('timestamp') or e.get('ts')
        if ts:
            try:
                entry_ts = datetime.fromisoformat(ts.replace('Z', '+00:00')).timestamp()
                if entry_ts < cutoff:
                    continue
            except:
                continue
        
        etype = e.get('type')
        emoji = e.get('emoji', '')
        
        if etype == 'reaction':
            if emoji in ['👍', '🔥', '👏', '❤️', '⭐']:
                positive += 1
            elif emoji in ['👎', '💤', '🤔']:
                negative += 1
        elif etype == 'reply':
            speed = e.get('replySpeed', '')
            if speed == 'fast':
                positive += 2
            elif speed == 'slow':
                negative += 1
        elif etype == 'instruction':
            positive += 2  # Direct engagement is very positive
    
    # Calculate multiplier
    score = positive - negative
    
    if score >= 3:
        return 0.6   # Very engaged - 40% shorter
    elif score >= 1:
        return 0.8   # Engaged - 20% shorter
    elif score <= -2:
        return 1.5   # Disengaged - 50% longer
    else:
        return 1.0   # Neutral

def calculate_day_multiplier(day: int) -> float:
    """
    Weekend = longer intervals (family time).
    Day: 0=Mon, 5=Sat, 6=Sun
    """
    if day >= 5:  # Weekend
        return 1.3  # 30% longer
    return 1.0

def calculate_actions_today_multiplier(state: dict) -> float:
    """
    If many actions already today, slow down.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if state.get("lastDate") != today:
        return 1.0  # New day, reset
    
    actions = state.get("actionsToday", 0)
    if actions >= 8:
        return 1.5  # Already very active, slow down
    elif actions >= 5:
        return 1.2
    return 1.0

def get_optimal_interval() -> int:
    """Calculate optimal interval for next action."""
    config = load_schedule_config()
    recent = load_recent_engagement()
    state = load_scheduler_state()
    hour = get_sgt_hour()
    day = get_day_of_week()
    
    # Calculate multipliers
    time_mult = calculate_time_multiplier(hour, config)
    engagement_mult = calculate_engagement_multiplier(recent)
    day_mult = calculate_day_multiplier(day)
    actions_mult = calculate_actions_today_multiplier(state)
    
    # Combined multiplier
    total_mult = time_mult * engagement_mult * day_mult * actions_mult
    
    # Calculate interval
    interval = int(BASE_INTERVAL * total_mult)
    
    # Clamp to bounds
    interval = max(MIN_INTERVAL, min(MAX_INTERVAL, interval))
    
    return interval

def log_action():
    """Log that an action was taken."""
    state = load_scheduler_state()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    if state.get("lastDate") != today:
        state["actionsToday"] = 1
        state["lastDate"] = today
    else:
        state["actionsToday"] = state.get("actionsToday", 0) + 1
    
    state["lastActionTs"] = datetime.now(timezone.utc).isoformat()
    save_scheduler_state(state)
    print(f"Logged action #{state['actionsToday']} for {today}")

def show_status():
    """Show current scheduling status."""
    config = load_schedule_config()
    recent = load_recent_engagement()
    state = load_scheduler_state()
    hour = get_sgt_hour()
    day = get_day_of_week()
    
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    print("=== Adaptive Scheduler Status ===")
    print(f"Current time: {hour:02d}:00 SGT ({days[day]})")
    print()
    
    time_mult = calculate_time_multiplier(hour, config)
    engagement_mult = calculate_engagement_multiplier(recent)
    day_mult = calculate_day_multiplier(day)
    actions_mult = calculate_actions_today_multiplier(state)
    
    print("Multipliers:")
    print(f"  Time of day:  {time_mult:.2f} {'(peak)' if time_mult < 1 else '(slow)' if time_mult > 1 else ''}")
    print(f"  Engagement:   {engagement_mult:.2f} {'(high)' if engagement_mult < 1 else '(low)' if engagement_mult > 1 else ''}")
    print(f"  Day of week:  {day_mult:.2f} {'(weekend)' if day_mult > 1 else ''}")
    print(f"  Actions today: {actions_mult:.2f} ({state.get('actionsToday', 0)} actions)")
    print()
    
    interval = get_optimal_interval()
    print(f"Optimal interval: {interval}s ({interval//60}m)")
    print(f"Range: {MIN_INTERVAL}s - {MAX_INTERVAL}s")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--status":
            show_status()
        elif sys.argv[1] == "--log-action":
            log_action()
        else:
            print(__doc__)
    else:
        # Default: output optimal interval
        print(get_optimal_interval())
