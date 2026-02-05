#!/usr/bin/env python3
"""
Goal Evaluation — Quality check for completed sub-goals

Runs evaluation loop to verify sub-goal quality before marking complete.

Usage:
    python3 scripts/goal-evaluate.py <goal_id> <sub_id>  # Evaluate specific sub-goal
    python3 scripts/goal-evaluate.py <goal_id> --all     # Evaluate all in-progress
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

SGT = ZoneInfo("Asia/Singapore")
GOALS_FILE = Path(__file__).parent.parent / "memory" / "active-goals.json"
EVALS_DIR = Path(__file__).parent.parent / "memory" / "goal-evals"

EVALS_DIR.mkdir(parents=True, exist_ok=True)

# Evaluation criteria by type
EVAL_CRITERIA = {
    "research": [
        "Are there 3+ credible sources?",
        "Is the information recent/relevant?",
        "Are key concepts explained clearly?",
        "Is there original synthesis, not just summary?",
    ],
    "execute": [
        "Is the deliverable complete?",
        "Does it meet the stated requirements?",
        "Is the quality acceptable?",
        "Are there obvious gaps or errors?",
    ],
    "verify": [
        "Were all checks performed?",
        "Are the findings documented?",
        "Were issues identified addressed?",
        "Is there confidence in the result?",
    ],
}


def get_eval_prompt(goal: dict, sub_goal: dict, result: str = None) -> str:
    """Generate evaluation prompt for LLM."""
    criteria = EVAL_CRITERIA.get(sub_goal.get("type", "execute"), EVAL_CRITERIA["execute"])
    
    prompt = f"""EVALUATE SUB-GOAL COMPLETION

Main Goal: {goal['description']}
Sub-Goal: {sub_goal['description']}
Type: {sub_goal.get('type', 'execute')}

{f"Result/Output: {result}" if result else "No result provided yet."}

Evaluation Criteria:
{chr(10).join(f"- {c}" for c in criteria)}

Score each criterion (1-5) and provide overall assessment:
- PASS: Ready to mark complete
- REVISE: Needs improvement (specify what)
- FAIL: Must redo

Output JSON:
{{
  "scores": {{"criterion_1": 4, ...}},
  "overall": "PASS|REVISE|FAIL",
  "feedback": "...",
  "next_steps": ["...", "..."]  // if REVISE or FAIL
}}
"""
    return prompt


def log_evaluation(goal_id: str, sub_id: str, evaluation: dict):
    """Log evaluation result."""
    eval_file = EVALS_DIR / f"{goal_id}.json"
    
    if eval_file.exists():
        data = json.loads(eval_file.read_text())
    else:
        data = {"goal_id": goal_id, "evaluations": []}
    
    data["evaluations"].append({
        "sub_id": sub_id,
        "time": datetime.now(SGT).strftime("%Y-%m-%d %H:%M SGT"),
        **evaluation
    })
    
    eval_file.write_text(json.dumps(data, indent=2))


def show_eval_prompt(goal_id: str, sub_id: str):
    """Show evaluation prompt for a sub-goal."""
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
    
    print(f"📊 Evaluation prompt for: {sub_goal['description'][:50]}...")
    print()
    print("-" * 50)
    print(get_eval_prompt(goal, sub_goal))
    print("-" * 50)
    print()
    print("To evaluate in daemon:")
    print("1. Get the result/output from the sub-goal execution")
    print("2. Run evaluation with the prompt above")
    print("3. If PASS → mark complete")
    print("4. If REVISE → iterate")
    print("5. Log: python3 scripts/goal-evaluate.py log <goal_id> <sub_id> <result>")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  goal-evaluate.py <goal_id> <sub_id>   # Show eval prompt")
        print("  goal-evaluate.py <goal_id> --all      # Show all in-progress")
        sys.exit(1)
    
    goal_id = sys.argv[1]
    
    if sys.argv[2] == "--all":
        data = json.loads(GOALS_FILE.read_text())
        for g in data["goals"]:
            if g["id"] == goal_id:
                in_progress = [s for s in g["sub_goals"] if s["status"] == "in_progress"]
                for s in in_progress:
                    show_eval_prompt(goal_id, s["id"])
                    print("\n" + "=" * 50 + "\n")
                break
    else:
        show_eval_prompt(goal_id, sys.argv[2])
