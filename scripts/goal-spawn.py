#!/usr/bin/env python3
"""
Goal Spawn — Spawn sub-agents for goal execution

Integrates with sessions_spawn to run sub-goals in parallel.

Usage:
    python3 scripts/goal-spawn.py <goal_id> <sub_id>
    python3 scripts/goal-spawn.py <goal_id> --all-pending
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

SGT = ZoneInfo("Asia/Singapore")
GOALS_FILE = Path(__file__).parent.parent / "memory" / "active-goals.json"


def get_spawn_task(goal: dict, sub_goal: dict) -> str:
    """Generate task prompt for spawned agent."""
    
    task = f"""GOAL EXECUTION TASK

Main Goal: {goal['description']}
Sub-Goal: {sub_goal['description']}
Type: {sub_goal.get('type', 'execute')}

Instructions:
1. Complete this specific sub-goal
2. Be thorough but focused
3. When done, output a clear summary of what was accomplished
4. If blocked, explain what's needed

Context from main goal:
- Progress so far: {goal['progress_pct']}%
- Other sub-goals: {[s['description'] for s in goal['sub_goals'] if s['id'] != sub_goal['id']]}

Execute now. Report results."""

    return task


def mark_spawned(goal_id: str, sub_id: str, session_key: str):
    """Mark sub-goal as spawned with session key."""
    data = json.loads(GOALS_FILE.read_text())
    
    for g in data["goals"]:
        if g["id"] == goal_id:
            for sub in g["sub_goals"]:
                if sub["id"] == sub_id:
                    sub["status"] = "in_progress"
                    sub["agent_session"] = session_key
                    sub["spawned_at"] = datetime.now(SGT).strftime("%Y-%m-%d %H:%M SGT")
                    break
            g["updated"] = datetime.now(SGT).strftime("%Y-%m-%d %H:%M SGT")
            break
    
    GOALS_FILE.write_text(json.dumps(data, indent=2))


def get_pending_sub_goals(goal_id: str) -> list:
    """Get all pending sub-goals for a goal."""
    data = json.loads(GOALS_FILE.read_text())
    
    for g in data["goals"]:
        if g["id"] == goal_id:
            return [s for s in g["sub_goals"] if s["status"] == "pending"]
    
    return []


def show_spawn_command(goal_id: str, sub_id: str):
    """Show the sessions_spawn command to use."""
    data = json.loads(GOALS_FILE.read_text())
    
    goal = None
    sub_goal = None
    
    for g in data["goals"]:
        if g["id"] == goal_id:
            goal = g
            for s in g["sub_goals"]:
                if s["id"] == sub_id:
                    sub_goal = s
                    break
            break
    
    if not goal or not sub_goal:
        print("Goal or sub-goal not found.")
        return
    
    task = get_spawn_task(goal, sub_goal)
    
    print(f"📤 Spawn command for sub-goal: {sub_goal['description']}")
    print()
    print("Use in daemon:")
    print("-" * 40)
    print(f'''sessions_spawn(
    task="""{task}""",
    model="anthropic/claude-sonnet-4-0",
    label="goal-{goal_id}-{sub_id}"
)''')
    print("-" * 40)
    print()
    print(f"After spawn, mark as in-progress:")
    print(f"  python3 scripts/goal-spawn.py mark {goal_id} {sub_id} <session_key>")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  goal-spawn.py <goal_id> <sub_id>      # Show spawn command")
        print("  goal-spawn.py <goal_id> --all-pending # Show all pending")
        print("  goal-spawn.py mark <goal_id> <sub_id> <session_key>  # Mark spawned")
        sys.exit(1)
    
    if sys.argv[1] == "mark":
        mark_spawned(sys.argv[2], sys.argv[3], sys.argv[4])
        print(f"✅ Marked {sys.argv[3]} as in-progress")
    elif sys.argv[2] == "--all-pending":
        pending = get_pending_sub_goals(sys.argv[1])
        print(f"Pending sub-goals for {sys.argv[1]}:")
        for p in pending:
            print(f"  ⬜ [{p['id']}] {p['description']}")
    else:
        show_spawn_command(sys.argv[1], sys.argv[2])
