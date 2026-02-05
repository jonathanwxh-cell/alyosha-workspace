#!/usr/bin/env python3
"""
Goal Heartbeat — Check goal progress during heartbeats

Surfaces active goals and their status. Identifies stalled goals.

Usage:
    python3 scripts/goal-heartbeat.py          # Check all active goals
    python3 scripts/goal-heartbeat.py --stale  # Only show stalled goals
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

SGT = ZoneInfo("Asia/Singapore")
GOALS_FILE = Path(__file__).parent.parent / "memory" / "active-goals.json"

STALE_HOURS = 24  # Goal is stale if no progress in 24h


def load_goals() -> list:
    """Load active goals."""
    if not GOALS_FILE.exists():
        return []
    data = json.loads(GOALS_FILE.read_text())
    return [g for g in data.get("goals", []) if g["status"] == "active"]


def parse_time(time_str: str) -> datetime:
    """Parse SGT time string."""
    try:
        return datetime.strptime(time_str, "%Y-%m-%d %H:%M SGT").replace(tzinfo=SGT)
    except:
        return datetime.now(SGT)


def is_stale(goal: dict) -> bool:
    """Check if goal has stalled."""
    updated = parse_time(goal.get("updated", goal.get("created", "")))
    return datetime.now(SGT) - updated > timedelta(hours=STALE_HOURS)


def get_next_action(goal: dict) -> str:
    """Determine next action for a goal."""
    pending = [s for s in goal.get("sub_goals", []) if s["status"] == "pending"]
    in_progress = [s for s in goal.get("sub_goals", []) if s["status"] == "in_progress"]
    
    if in_progress:
        return f"Check on: {in_progress[0]['description'][:50]}..."
    elif pending:
        return f"Start: {pending[0]['description'][:50]}..."
    else:
        return "All sub-goals complete — mark goal done"


def check_goals(stale_only: bool = False) -> str:
    """Check goal status and return summary."""
    goals = load_goals()
    
    if not goals:
        return "No active goals."
    
    if stale_only:
        goals = [g for g in goals if is_stale(g)]
        if not goals:
            return "No stale goals."
    
    lines = [f"📋 Active Goals ({len(goals)}):"]
    
    for g in goals:
        status_icon = "⚠️" if is_stale(g) else "🔄"
        lines.append(f"\n{status_icon} {g['description'][:60]}")
        lines.append(f"   Progress: {g['progress_pct']}% | ID: {g['id']}")
        
        # Sub-goal summary
        total = len(g.get("sub_goals", []))
        complete = sum(1 for s in g.get("sub_goals", []) if s["status"] == "complete")
        in_progress = sum(1 for s in g.get("sub_goals", []) if s["status"] == "in_progress")
        
        if total > 0:
            lines.append(f"   Sub-goals: {complete}/{total} done, {in_progress} in progress")
        
        # Next action
        next_action = get_next_action(g)
        lines.append(f"   Next: {next_action}")
    
    return "\n".join(lines)


def heartbeat_check() -> dict:
    """Return structured data for heartbeat integration."""
    goals = load_goals()
    
    return {
        "active_count": len(goals),
        "stale_count": sum(1 for g in goals if is_stale(g)),
        "total_progress": sum(g["progress_pct"] for g in goals) // len(goals) if goals else 0,
        "needs_attention": [g["id"] for g in goals if is_stale(g)],
        "summary": check_goals()
    }


if __name__ == "__main__":
    stale_only = "--stale" in sys.argv
    print(check_goals(stale_only))
