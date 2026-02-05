#!/usr/bin/env python3
"""
Goal Competency Audit

Scans all goals for competency gaps and identifies research priorities.
Works for any goal that has a competencies.md file.

Usage:
  python3 scripts/goal-competency-audit.py scan      # List all gaps
  python3 scripts/goal-competency-audit.py priority  # Get top research priority
  python3 scripts/goal-competency-audit.py update GOAL SKILL LEVEL  # Update a skill level
"""

import sys
import re
from pathlib import Path

GOALS_DIR = Path.home() / ".openclaw/workspace/memory/goals"

def parse_competencies(filepath):
    """Parse a competencies.md file and extract skills with levels."""
    if not filepath.exists():
        return None
    
    content = filepath.read_text()
    skills = []
    
    # Match pattern: ### Skill Name followed by **Level:** X/10
    pattern = r'###\s+(.+?)\n.*?\*\*Level:\*\*\s+(\d+)/10'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for skill_name, level in matches:
        skills.append({
            'skill': skill_name.strip(),
            'level': int(level),
            'max': 10
        })
    
    return skills

def scan_all_goals():
    """Scan all goals and return competency data."""
    results = {}
    
    if not GOALS_DIR.exists():
        return results
    
    for goal_dir in GOALS_DIR.iterdir():
        if goal_dir.is_dir():
            comp_file = goal_dir / "competencies.md"
            skills = parse_competencies(comp_file)
            if skills:
                results[goal_dir.name] = skills
    
    return results

def get_priority_gap():
    """Find the lowest-scored skill across all goals."""
    all_goals = scan_all_goals()
    
    if not all_goals:
        return None
    
    lowest = None
    for goal_name, skills in all_goals.items():
        for skill in skills:
            if lowest is None or skill['level'] < lowest['level']:
                lowest = {
                    'goal': goal_name,
                    'skill': skill['skill'],
                    'level': skill['level']
                }
    
    return lowest

def print_scan():
    """Print all competency gaps."""
    all_goals = scan_all_goals()
    
    if not all_goals:
        print("No goals with competencies.md found.")
        return
    
    print("📊 **Goal Competency Audit**\n")
    
    for goal_name, skills in all_goals.items():
        print(f"**{goal_name.upper()}**")
        # Sort by level (lowest first)
        sorted_skills = sorted(skills, key=lambda x: x['level'])
        for s in sorted_skills:
            bar = "█" * s['level'] + "░" * (10 - s['level'])
            emoji = "🔴" if s['level'] <= 3 else "🟡" if s['level'] <= 6 else "🟢"
            print(f"  {emoji} {s['skill']}: {s['level']}/10 [{bar}]")
        print()
    
    priority = get_priority_gap()
    if priority:
        print(f"**Priority research:** {priority['goal']}/{priority['skill']} (level {priority['level']}/10)")

def print_priority():
    """Print just the top priority."""
    priority = get_priority_gap()
    
    if not priority:
        print("No competency gaps found.")
        return
    
    print(f"PRIORITY: {priority['goal']} - {priority['skill']} (currently {priority['level']}/10)")
    print(f"\nResearch this competency to improve goal performance.")

def main():
    if len(sys.argv) < 2:
        print("Usage: goal-competency-audit.py [scan|priority|update]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "scan":
        print_scan()
    elif cmd == "priority":
        print_priority()
    elif cmd == "update":
        if len(sys.argv) < 5:
            print("Usage: goal-competency-audit.py update GOAL SKILL LEVEL")
            sys.exit(1)
        # TODO: Implement update
        print("Update not yet implemented - edit competencies.md directly")
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
