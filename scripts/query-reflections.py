#!/usr/bin/env python3
"""
Query past reflections for relevant lessons before similar tasks.
Part of enhanced Reflexion implementation.

Usage:
  python scripts/query-reflections.py "research" "nvidia"
  python scripts/query-reflections.py --category meta
  python scripts/query-reflections.py --recent 5
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta

REFLECTIONS_PATH = Path(__file__).parent.parent / "memory" / "reflections.jsonl"

def load_reflections():
    """Load all reflections from JSONL file."""
    if not REFLECTIONS_PATH.exists():
        return []
    
    reflections = []
    with open(REFLECTIONS_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    reflections.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return reflections

def search_reflections(reflections, keywords=None, category=None, recent_days=None):
    """Filter reflections by keywords, category, or recency."""
    results = reflections
    
    # Filter by recency
    if recent_days:
        cutoff = datetime.utcnow()
        cutoff = cutoff - timedelta(days=recent_days)
        filtered = []
        for r in results:
            ts = r.get('timestamp', '')
            try:
                # Parse and make naive for comparison
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                dt_naive = dt.replace(tzinfo=None)
                if dt_naive > cutoff:
                    filtered.append(r)
            except:
                filtered.append(r)  # Keep if unparseable
        results = filtered
    
    # Filter by category
    if category:
        results = [
            r for r in results 
            if r.get('category', '').lower() == category.lower() or
               category.lower() in r.get('tags', [])
        ]
    
    # Filter by keywords (search in task, reflection, lesson, tags)
    if keywords:
        filtered = []
        for r in results:
            searchable = ' '.join([
                r.get('task', ''),
                r.get('reflection', ''),
                r.get('lesson', ''),
                ' '.join(r.get('tags', []))
            ]).lower()
            if all(kw.lower() in searchable for kw in keywords):
                filtered.append(r)
        results = filtered
    
    return results

def format_output(reflections):
    """Format reflections for display."""
    if not reflections:
        print("No matching reflections found.")
        return
    
    print(f"\n📚 Found {len(reflections)} relevant reflection(s):\n")
    print("-" * 60)
    
    for r in reflections:
        timestamp = r.get('timestamp', 'unknown')[:10]
        task = r.get('task', 'unknown')
        outcome = r.get('outcome', '?')
        lesson = r.get('lesson', r.get('reflection', 'no lesson'))
        
        outcome_emoji = {'success': '✅', 'partial': '⚠️', 'failure': '❌'}.get(outcome, '❓')
        
        print(f"{outcome_emoji} [{timestamp}] {task}")
        print(f"   💡 {lesson}")
        print()

def main():
    parser = argparse.ArgumentParser(description='Query past reflections')
    parser.add_argument('keywords', nargs='*', help='Keywords to search for')
    parser.add_argument('--category', '-c', help='Filter by category')
    parser.add_argument('--recent', '-r', type=int, help='Only show last N days')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    reflections = load_reflections()
    results = search_reflections(
        reflections,
        keywords=args.keywords if args.keywords else None,
        category=args.category,
        recent_days=args.recent
    )
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        format_output(results)

if __name__ == '__main__':
    main()
