#!/usr/bin/env python3
"""
Goal Decomposition — LLM-powered goal breakdown

Takes a high-level goal and decomposes it into actionable sub-goals.
Uses structured output for reliable parsing.

Usage:
    python3 scripts/goal-decompose.py "Write a Substack post about quantum biology"
    python3 scripts/goal-decompose.py --goal-id abc123  # Decompose existing goal
"""

import json
import sys
from pathlib import Path

# Decomposition prompt template
DECOMPOSE_PROMPT = """Break down this goal into 3-7 concrete sub-goals.

GOAL: {goal}

Requirements:
- Each sub-goal should be actionable and completable
- Order by dependency (what needs to happen first)
- Include research, execution, and verification steps
- Be specific, not vague

Output as JSON array:
[
  {{"step": 1, "description": "...", "type": "research|execute|verify", "can_parallel": false}},
  ...
]

Only output the JSON array, nothing else."""


def decompose_goal(goal_description: str) -> list:
    """
    Decompose a goal into sub-goals.
    
    This function is meant to be called by the daemon (Opus) which will
    use its reasoning to break down the goal.
    
    Returns a suggested decomposition structure.
    """
    # This is a template - actual decomposition happens in the LLM
    print(f"📋 Goal to decompose: {goal_description}")
    print()
    print("Suggested decomposition approach:")
    print("1. Identify the core deliverable")
    print("2. Work backwards - what's needed to produce it?")
    print("3. Identify research/information gathering steps")
    print("4. Identify execution/creation steps")
    print("5. Add verification/review steps")
    print()
    print("Prompt for LLM:")
    print("-" * 40)
    print(DECOMPOSE_PROMPT.format(goal=goal_description))
    print("-" * 40)
    
    return []


def add_sub_goals_to_tracker(goal_id: str, sub_goals: list):
    """Add decomposed sub-goals to the goal tracker."""
    import uuid
    from datetime import datetime
    from zoneinfo import ZoneInfo
    
    SGT = ZoneInfo("Asia/Singapore")
    GOALS_FILE = Path(__file__).parent.parent / "memory" / "active-goals.json"
    
    if not GOALS_FILE.exists():
        print("No goals file found.")
        return False
    
    data = json.loads(GOALS_FILE.read_text())
    
    for g in data["goals"]:
        if g["id"] == goal_id:
            for i, sub in enumerate(sub_goals):
                sub_goal = {
                    "id": str(uuid.uuid4())[:8],
                    "description": sub.get("description", sub) if isinstance(sub, dict) else sub,
                    "status": "pending",
                    "step": sub.get("step", i + 1) if isinstance(sub, dict) else i + 1,
                    "type": sub.get("type", "execute") if isinstance(sub, dict) else "execute",
                    "can_parallel": sub.get("can_parallel", False) if isinstance(sub, dict) else False,
                    "created": datetime.now(SGT).strftime("%Y-%m-%d %H:%M SGT"),
                    "agent_session": None
                }
                g["sub_goals"].append(sub_goal)
            
            g["updated"] = datetime.now(SGT).strftime("%Y-%m-%d %H:%M SGT")
            break
    
    GOALS_FILE.write_text(json.dumps(data, indent=2))
    print(f"✅ Added {len(sub_goals)} sub-goals to {goal_id}")
    return True


# Integration with main daemon
DAEMON_DECOMPOSE_INSTRUCTION = """
To decompose a goal, use this pattern:

1. Get the goal:
   python3 scripts/goal-tracker.py show <goal_id>

2. Think through the decomposition:
   - What's the deliverable?
   - What research is needed?
   - What are the execution steps?
   - How to verify quality?

3. Add sub-goals via Python:
   ```python
   import json
   from pathlib import Path
   
   sub_goals = [
       {"description": "Research X", "type": "research", "step": 1},
       {"description": "Build Y", "type": "execute", "step": 2},
       {"description": "Test Z", "type": "verify", "step": 3},
   ]
   
   # Then call add_sub_goals_to_tracker(goal_id, sub_goals)
   ```

4. Or spawn a Sonnet agent to do the decomposition:
   sessions_spawn(task="Decompose this goal into sub-goals: <goal>", model="sonnet")
"""


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: goal-decompose.py \"goal description\"")
        print("       goal-decompose.py --goal-id <id>")
        print()
        print(DAEMON_DECOMPOSE_INSTRUCTION)
        sys.exit(1)
    
    if sys.argv[1] == "--goal-id":
        # Load goal from tracker
        goal_id = sys.argv[2]
        GOALS_FILE = Path(__file__).parent.parent / "memory" / "active-goals.json"
        data = json.loads(GOALS_FILE.read_text())
        
        for g in data["goals"]:
            if g["id"] == goal_id:
                decompose_goal(g["description"])
                break
    else:
        goal = " ".join(sys.argv[1:])
        decompose_goal(goal)
