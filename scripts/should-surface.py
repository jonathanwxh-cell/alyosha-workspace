#!/usr/bin/env python3
"""
Adaptive scheduling decision: Should I surface a message now?

Factors considered:
1. Time of day (SGT)
2. Day of week (weekend = lighter touch)
3. Recent engagement (backoff if no replies)
4. Active conversation (delay if chatting)
5. Time since last surface

Returns: JSON with decision + reasoning
"""

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

WORKSPACE = Path(os.environ.get("WORKSPACE", "/home/ubuntu/.openclaw/workspace"))
SCHEDULING_FILE = WORKSPACE / "memory/scheduling-intelligence.json"
HEARTBEAT_STATE = WORKSPACE / "memory/heartbeat-state.json"
FEEDBACK_LOG = WORKSPACE / "memory/feedback-log.jsonl"

def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return {}

def load_jsonl(path):
    entries = []
    try:
        with open(path) as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
    except:
        pass
    return entries

def get_sgt_now():
    """Get current time in SGT (UTC+8)"""
    return datetime.now(timezone.utc) + timedelta(hours=8)

def calculate_recent_engagement(feedback_log, n=10):
    """Calculate reply rate from last N surfaces"""
    surfaces = [e for e in feedback_log if e.get("type") in ["surface", "reply", "reaction"]]
    if len(surfaces) < 3:
        return 0.5  # Default neutral
    
    recent = surfaces[-n:]
    replies = sum(1 for e in recent if e.get("type") in ["reply", "reaction"])
    return replies / len(recent)

def check_active_conversation(feedback_log, window_minutes=30):
    """Check if there's been recent engagement (active conversation)"""
    if not feedback_log:
        return False
    
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    for entry in reversed(feedback_log[-10:]):
        ts = entry.get("ts") or entry.get("timestamp")
        if ts:
            try:
                entry_time = datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(tzinfo=None)
                if (now - entry_time).total_seconds() < window_minutes * 60:
                    if entry.get("type") in ["reply", "reaction"]:
                        return True
            except:
                pass
    return False

def get_surfaces_without_engagement(feedback_log):
    """Count consecutive surfaces without reply OR reaction"""
    count = 0
    for entry in reversed(feedback_log):
        if entry.get("type") == "surface":
            count += 1
        elif entry.get("type") in ["reply", "reaction"]:
            # Any engagement signal breaks the streak
            break
    return count

def should_surface():
    now_sgt = get_sgt_now()
    hour = now_sgt.hour
    is_weekend = now_sgt.weekday() >= 5
    
    scheduling = load_json(SCHEDULING_FILE)
    heartbeat = load_json(HEARTBEAT_STATE)
    feedback = load_jsonl(FEEDBACK_LOG)
    
    decision = {
        "should_surface": True,
        "confidence": 1.0,
        "reasons": [],
        "adjustments": []
    }
    
    # 1. Check sleep hours (hard block)
    sleep_hours = list(range(23, 24)) + list(range(0, 8))
    if hour in sleep_hours:
        decision["should_surface"] = False
        decision["confidence"] = 0.9
        decision["reasons"].append(f"Sleep hours ({hour}:xx SGT)")
        return decision
    
    # 2. Check active conversation
    if check_active_conversation(feedback, 30):
        decision["adjustments"].append("Active conversation - consider delaying")
        decision["confidence"] *= 0.7
    
    # 3. Check backoff (surfaces without engagement - reply or reaction)
    no_engagement_count = get_surfaces_without_engagement(feedback)
    adaptive = scheduling.get("adaptiveScheduling", {})
    fatigue = adaptive.get("messageFatigue", {})
    threshold = fatigue.get("maxUnrepliedSurfaces", 3)
    
    if no_engagement_count >= threshold:
        decision["adjustments"].append(f"Message fatigue: {no_engagement_count} surfaces without engagement (threshold: {threshold})")
        decision["confidence"] *= 0.3  # Heavy penalty
        decision["fatigue_detected"] = True
    
    # 4. Weekend adjustment
    if is_weekend:
        weekend_weight = adaptive.get("dayOfWeek", {}).get("weekend", {}).get("surfaceWeight", 0.7)
        decision["adjustments"].append(f"Weekend: surface weight {weekend_weight}")
        decision["confidence"] *= weekend_weight
    
    # 5. Recent engagement rate
    engagement_rate = calculate_recent_engagement(feedback, 10)
    decision["engagement_rate"] = round(engagement_rate, 2)
    if engagement_rate < 0.3:
        decision["adjustments"].append(f"Low recent engagement ({engagement_rate:.0%})")
        decision["confidence"] *= 0.8
    
    # Final decision
    if decision["confidence"] < 0.5:
        decision["should_surface"] = False
        decision["reasons"].append(f"Confidence too low: {decision['confidence']:.2f}")
    else:
        decision["reasons"].append(f"OK to surface (confidence: {decision['confidence']:.2f})")
    
    decision["timestamp_sgt"] = now_sgt.strftime("%Y-%m-%d %H:%M")
    decision["hour_sgt"] = hour
    decision["is_weekend"] = is_weekend
    
    return decision

if __name__ == "__main__":
    result = should_surface()
    print(json.dumps(result, indent=2))
