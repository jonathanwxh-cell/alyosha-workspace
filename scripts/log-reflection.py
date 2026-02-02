#!/usr/bin/env python3
"""
Log a reflection after completing a task.
Part of Reflexion pattern implementation.

Usage:
  python scripts/log-reflection.py "task_name" "success|partial|failure" "what happened" "lesson learned"
  python scripts/log-reflection.py --interactive
  
Options:
  --category CAT    Category (research|build|explore|meta|tools)
  --tags TAG1,TAG2  Comma-separated tags
"""

import json
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path

REFLECTIONS_PATH = Path(__file__).parent.parent / "memory" / "reflections.jsonl"

def log_reflection(task: str, outcome: str, reflection: str, lesson: str, 
                   category: str = None, tags: list = None):
    """Append a reflection to the JSONL file."""
    
    entry = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "task": task,
        "outcome": outcome,
        "reflection": reflection,
        "lesson": lesson
    }
    
    if category:
        entry["category"] = category
    if tags:
        entry["tags"] = tags
    
    # Ensure directory exists
    REFLECTIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Append to file
    with open(REFLECTIONS_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    print(f"✓ Logged reflection for '{task}'")
    print(f"  Outcome: {outcome}")
    print(f"  Lesson: {lesson}")

def interactive_mode():
    """Prompt user for reflection details."""
    print("=== Log Reflection ===\n")
    
    task = input("Task name: ").strip()
    if not task:
        print("Task name required")
        return
    
    outcome = input("Outcome (success/partial/failure): ").strip().lower()
    if outcome not in ("success", "partial", "failure"):
        outcome = "success"
    
    reflection = input("What happened? ").strip()
    lesson = input("Lesson learned: ").strip()
    
    category = input("Category (research/build/explore/meta/tools) [optional]: ").strip() or None
    tags_input = input("Tags (comma-separated) [optional]: ").strip()
    tags = [t.strip() for t in tags_input.split(",")] if tags_input else None
    
    log_reflection(task, outcome, reflection, lesson, category, tags)

def main():
    parser = argparse.ArgumentParser(description="Log a task reflection")
    parser.add_argument("task", nargs="?", help="Task name")
    parser.add_argument("outcome", nargs="?", help="success|partial|failure")
    parser.add_argument("reflection", nargs="?", help="What happened")
    parser.add_argument("lesson", nargs="?", help="Lesson learned")
    parser.add_argument("--category", "-c", help="Category")
    parser.add_argument("--tags", "-t", help="Comma-separated tags")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
        return
    
    if not all([args.task, args.outcome, args.reflection, args.lesson]):
        print("Usage: log-reflection.py TASK OUTCOME REFLECTION LESSON")
        print("   or: log-reflection.py --interactive")
        sys.exit(1)
    
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else None
    
    log_reflection(
        args.task,
        args.outcome,
        args.reflection,
        args.lesson,
        args.category,
        tags
    )

if __name__ == "__main__":
    main()
