#!/usr/bin/env python3
"""
Feedback Signal Tracker

Captures positive/negative engagement signals to improve daemon behavior.
Addresses gap: "Not capturing positive feedback signals"

Usage:
    python3 scripts/track-feedback.py positive "Great insight on DeepSeek"
    python3 scripts/track-feedback.py negative "Too many messages"
    python3 scripts/track-feedback.py engagement "Jon replied within 30min"
    python3 scripts/track-feedback.py --stats
    python3 scripts/track-feedback.py --recent 10
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from collections import Counter

FEEDBACK_FILE = Path.home() / ".openclaw/workspace/memory/feedback-log.jsonl"

def log_feedback(signal_type, context, source="manual"):
    """Log a feedback signal."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "type": signal_type,  # positive, negative, engagement, neutral
        "context": context,
        "source": source  # manual, reaction, reply, silence
    }
    
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(FEEDBACK_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    emoji = {"positive": "👍", "negative": "👎", "engagement": "💬", "neutral": "😐"}.get(signal_type, "📝")
    print(f"{emoji} Logged {signal_type}: {context[:50]}...")

def load_feedback():
    """Load all feedback entries."""
    if not FEEDBACK_FILE.exists():
        return []
    
    entries = []
    with open(FEEDBACK_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries

def show_stats():
    """Show feedback statistics."""
    entries = load_feedback()
    
    if not entries:
        print("No feedback recorded yet.")
        return
    
    types = Counter(e.get("type") for e in entries)
    sources = Counter(e.get("source") for e in entries)
    
    total = len(entries)
    positive = types.get("positive", 0)
    negative = types.get("negative", 0)
    engagement = types.get("engagement", 0)
    
    print("📊 Feedback Statistics")
    print("=" * 40)
    print(f"Total signals: {total}")
    print(f"👍 Positive: {positive} ({100*positive/total:.0f}%)" if total else "")
    print(f"👎 Negative: {negative} ({100*negative/total:.0f}%)" if total else "")
    print(f"💬 Engagement: {engagement} ({100*engagement/total:.0f}%)" if total else "")
    print()
    print("By source:")
    for source, count in sources.most_common():
        print(f"  {source}: {count}")
    
    # Sentiment score
    if positive + negative > 0:
        sentiment = (positive - negative) / (positive + negative)
        print(f"\nSentiment score: {sentiment:+.2f} (-1 to +1)")

def show_recent(n=10):
    """Show recent feedback."""
    entries = load_feedback()
    
    if not entries:
        print("No feedback recorded yet.")
        return
    
    print(f"📋 Last {n} feedback signals:\n")
    for entry in entries[-n:]:
        ts = entry.get("timestamp", "")[:16]
        sig_type = entry.get("type", "?")
        context = entry.get("context", "")[:60]
        emoji = {"positive": "👍", "negative": "👎", "engagement": "💬"}.get(sig_type, "📝")
        print(f"{emoji} [{ts}] {context}")

def main():
    args = sys.argv[1:]
    
    if not args or "--help" in args:
        print(__doc__)
        return
    
    if "--stats" in args:
        show_stats()
        return
    
    if "--recent" in args:
        n = 10
        idx = args.index("--recent")
        if idx + 1 < len(args):
            try:
                n = int(args[idx + 1])
            except ValueError:
                pass
        show_recent(n)
        return
    
    # Log feedback: type context
    if len(args) >= 2:
        signal_type = args[0].lower()
        context = " ".join(args[1:])
        
        if signal_type not in ["positive", "negative", "engagement", "neutral"]:
            print(f"Unknown signal type: {signal_type}")
            print("Valid types: positive, negative, engagement, neutral")
            return
        
        log_feedback(signal_type, context)

if __name__ == "__main__":
    main()
