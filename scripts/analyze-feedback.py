#!/usr/bin/env python3
"""
analyze-feedback.py - Analyze feedback patterns from feedback-log.jsonl
Run weekly to identify what works and what doesn't.
"""

import json
from collections import Counter, defaultdict
from datetime import datetime
import sys
import os

def load_feedback(path="memory/feedback-log.jsonl"):
    entries = []
    if not os.path.exists(path):
        return entries
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries

def analyze(entries):
    if not entries:
        print("No feedback entries yet.")
        return
    
    print(f"=== Feedback Analysis ({len(entries)} entries) ===\n")
    
    # Reactions by emoji
    reactions = [e for e in entries if e.get('type') == 'reaction']
    if reactions:
        print("## Reactions by Emoji")
        emoji_counts = Counter(e.get('emoji', '?') for e in reactions)
        for emoji, count in emoji_counts.most_common():
            print(f"  {emoji}: {count}")
        print()
    
    # Reactions by category
    if reactions:
        print("## Positive Reactions (👍🔥⭐) by Category")
        positive = [e for e in reactions if e.get('emoji') in ['👍', '🔥', '⭐']]
        cat_counts = Counter(e.get('category', 'unknown') for e in positive)
        for cat, count in cat_counts.most_common():
            print(f"  {cat}: {count}")
        print()
    
    # Replies by category
    replies = [e for e in entries if e.get('type') == 'reply']
    if replies:
        print("## Replies by Category")
        cat_counts = Counter(e.get('category', 'unknown') for e in replies)
        for cat, count in cat_counts.most_common():
            print(f"  {cat}: {count}")
        print()
        
        # Reply speed
        print("## Reply Speed Distribution")
        speed_counts = Counter(e.get('replySpeed', 'unknown') for e in replies)
        for speed, count in speed_counts.most_common():
            print(f"  {speed}: {count}")
        print()
    
    # Hour distribution
    print("## Activity by Hour (SGT)")
    hours = [e.get('hourSGT') for e in entries if e.get('hourSGT') is not None]
    if hours:
        hour_counts = Counter(hours)
        for hour in sorted(hour_counts.keys()):
            bar = '█' * hour_counts[hour]
            print(f"  {hour:02d}:00 {bar} ({hour_counts[hour]})")
    print()
    
    # Negative signals
    negative = [e for e in reactions if e.get('emoji') in ['👎', '💤']]
    if negative:
        print("## ⚠️ Negative Signals")
        for e in negative:
            print(f"  {e.get('emoji')} on {e.get('topic', 'unknown')} ({e.get('category', '?')})")
    else:
        print("## ✅ No negative signals yet")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "memory/feedback-log.jsonl"
    entries = load_feedback(path)
    analyze(entries)
