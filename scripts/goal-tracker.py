#!/usr/bin/env python3
"""
Goal Tracker — Persistent goal management with sub-goal decomposition

Based on research:
- HTN (Hierarchical Task Networks) for decomposition
- OpenAI Agents SDK patterns for orchestration
- BabyAGI lessons: step limits, state persistence, avoid over-complexity

Usage:
    python3 scripts/goal-tracker.py add "Write Substack post about quantum biology"
    python3 scripts/goal-tracker.py list
    python3 scripts/goal-tracker.py show <goal_id>
    python3 scripts/goal-tracker.py plan <goal_id>          # Decompose into sub-goals
    python3 scripts/goal-tracker.py progress <goal_id>      # Check progress
    python3 scripts/goal-tracker.py complete <goal_id> [sub_id]  # Mark complete
    python3 scripts/goal-tracker.py spawn <goal_id> <sub_id>     # Spawn agent for sub-goal
"""

import json
import sys
import uuid
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

SGT = ZoneInfo("Asia/Singapore")
GOALS_FILE = Path(__file__).parent.parent / "memory" / "active-goals.json"
PROGRESS_DIR = Path(__file__).parent.parent / "memory" / "goal-progress"

# Ensure directories exist
GOALS_FILE.parent.mkdir(parents=True, exist_ok=True)
PROGRESS_DIR.mkdir(parents=True, exist_ok=True)


def load_goals() -> dict:
    """Load active goals."""
    if GOALS_FILE.exists():
        return json.loads(GOALS_FILE.read_text())
    return {"goals": [], "version": 1}


def save_goals(data: dict):
    """Save goals."""
    GOALS_FILE.write_text(json.dumps(data, indent=2))


def now_sgt() -> str:
    """Current time in SGT."""
    return datetime.now(SGT).strftime("%Y-%m-%d %H:%M SGT")


def generate_id() -> str:
    """Short unique ID."""
    return str(uuid.uuid4())[:8]


def add_goal(description: str) -> dict:
    """Add a new goal."""
    data = load_goals()
    
    goal = {
        "id": generate_id(),
        "description": description,
        "status": "active",
        "created": now_sgt(),
        "updated": now_sgt(),
        "sub_goals": [],
        "progress_pct": 0,
        "notes": []
    }
    
    data["goals"].append(goal)
    save_goals(data)
    
    # Create progress file
    progress_file = PROGRESS_DIR / f"{goal['id']}.json"
    progress_file.write_text(json.dumps({
        "goal_id": goal["id"],
        "events": [{"time": now_sgt(), "event": "created", "description": description}]
    }, indent=2))
    
    return goal


def list_goals(show_all: bool = False) -> list:
    """List goals."""
    data = load_goals()
    goals = data.get("goals", [])
    
    if not show_all:
        goals = [g for g in goals if g["status"] == "active"]
    
    return goals


def get_goal(goal_id: str) -> dict:
    """Get a specific goal."""
    data = load_goals()
    for g in data.get("goals", []):
        if g["id"] == goal_id:
            return g
    return None


def add_sub_goals(goal_id: str, sub_goals: list):
    """Add sub-goals to a goal."""
    data = load_goals()
    
    for g in data["goals"]:
        if g["id"] == goal_id:
            for desc in sub_goals:
                sub = {
                    "id": generate_id(),
                    "description": desc,
                    "status": "pending",
                    "created": now_sgt(),
                    "agent_session": None
                }
                g["sub_goals"].append(sub)
            g["updated"] = now_sgt()
            break
    
    save_goals(data)
    log_progress(goal_id, "sub_goals_added", f"Added {len(sub_goals)} sub-goals")


def complete_sub_goal(goal_id: str, sub_id: str, result: str = None):
    """Mark a sub-goal complete."""
    data = load_goals()
    
    for g in data["goals"]:
        if g["id"] == goal_id:
            for sub in g["sub_goals"]:
                if sub["id"] == sub_id:
                    sub["status"] = "complete"
                    sub["completed"] = now_sgt()
                    if result:
                        sub["result"] = result
                    break
            
            # Update progress percentage
            total = len(g["sub_goals"])
            complete = sum(1 for s in g["sub_goals"] if s["status"] == "complete")
            g["progress_pct"] = int((complete / total) * 100) if total > 0 else 0
            g["updated"] = now_sgt()
            
            # Check if all complete
            if g["progress_pct"] == 100:
                g["status"] = "complete"
            
            break
    
    save_goals(data)
    log_progress(goal_id, "sub_goal_complete", f"Completed: {sub_id}")


def complete_goal(goal_id: str, summary: str = None):
    """Mark entire goal complete."""
    data = load_goals()
    
    for g in data["goals"]:
        if g["id"] == goal_id:
            g["status"] = "complete"
            g["completed"] = now_sgt()
            g["progress_pct"] = 100
            if summary:
                g["summary"] = summary
            break
    
    save_goals(data)
    log_progress(goal_id, "goal_complete", summary or "Goal completed")


def log_progress(goal_id: str, event: str, details: str):
    """Log progress event."""
    progress_file = PROGRESS_DIR / f"{goal_id}.json"
    
    if progress_file.exists():
        data = json.loads(progress_file.read_text())
    else:
        data = {"goal_id": goal_id, "events": []}
    
    data["events"].append({
        "time": now_sgt(),
        "event": event,
        "details": details
    })
    
    progress_file.write_text(json.dumps(data, indent=2))


def record_spawn(goal_id: str, sub_id: str, session_key: str):
    """Record that a sub-agent was spawned."""
    data = load_goals()
    
    for g in data["goals"]:
        if g["id"] == goal_id:
            for sub in g["sub_goals"]:
                if sub["id"] == sub_id:
                    sub["agent_session"] = session_key
                    sub["status"] = "in_progress"
                    sub["spawned"] = now_sgt()
                    break
            g["updated"] = now_sgt()
            break
    
    save_goals(data)
    log_progress(goal_id, "agent_spawned", f"Sub-goal {sub_id} → session {session_key}")


def format_goal(goal: dict) -> str:
    """Format goal for display."""
    lines = [
        f"📎 Goal: {goal['description']}",
        f"   ID: {goal['id']} | Status: {goal['status']} | Progress: {goal['progress_pct']}%",
        f"   Created: {goal['created']}"
    ]
    
    if goal.get("sub_goals"):
        lines.append("   Sub-goals:")
        for sub in goal["sub_goals"]:
            status_icon = {"pending": "⬜", "in_progress": "🔄", "complete": "✅"}.get(sub["status"], "❓")
            lines.append(f"     {status_icon} [{sub['id']}] {sub['description']}")
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: goal-tracker.py <command> [args]")
        print("Commands: add, list, show, plan, progress, complete, spawn")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "add":
        if len(sys.argv) < 3:
            print("Usage: goal-tracker.py add \"description\"")
            return
        goal = add_goal(" ".join(sys.argv[2:]))
        print(f"✅ Created goal: {goal['id']}")
        print(format_goal(goal))
    
    elif cmd == "list":
        goals = list_goals()
        if not goals:
            print("No active goals.")
        else:
            print(f"📋 Active Goals ({len(goals)}):\n")
            for g in goals:
                print(format_goal(g))
                print()
    
    elif cmd == "show":
        if len(sys.argv) < 3:
            print("Usage: goal-tracker.py show <goal_id>")
            return
        goal = get_goal(sys.argv[2])
        if goal:
            print(format_goal(goal))
        else:
            print("Goal not found.")
    
    elif cmd == "complete":
        if len(sys.argv) < 3:
            print("Usage: goal-tracker.py complete <goal_id> [sub_id]")
            return
        goal_id = sys.argv[2]
        if len(sys.argv) >= 4:
            complete_sub_goal(goal_id, sys.argv[3])
            print(f"✅ Sub-goal {sys.argv[3]} marked complete")
        else:
            complete_goal(goal_id)
            print(f"✅ Goal {goal_id} marked complete")
    
    elif cmd == "plan":
        print("Plan command requires LLM. Use in main session:")
        print("  1. Show goal: python3 scripts/goal-tracker.py show <id>")
        print("  2. Ask daemon to decompose into sub-goals")
        print("  3. Add sub-goals via Python or daemon")
    
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
