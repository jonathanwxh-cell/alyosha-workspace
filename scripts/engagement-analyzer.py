#!/usr/bin/env python3
"""
Engagement Analyzer - Track what surfaces get engagement
Run: python3 scripts/engagement-analyzer.py [report|topics|timing]
"""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

FEEDBACK_LOG = Path("memory/feedback-log.jsonl")

def load_feedback():
    if not FEEDBACK_LOG.exists():
        return []
    entries = []
    for line in FEEDBACK_LOG.read_text().splitlines():
        if line.strip():
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries

def analyze_by_topic(entries):
    """Which topics get engagement?"""
    topics = defaultdict(lambda: {"surfaces": 0, "engaged": 0})
    
    for e in entries:
        topic = e.get("topic", "unknown")
        if e.get("type") == "surface" or "msgId" in e:
            topics[topic]["surfaces"] += 1
            if e.get("gotReply") == True or e.get("signal") == "👍":
                topics[topic]["engaged"] += 1
        elif e.get("type") == "reaction" or e.get("signal") == "👍":
            # Standalone engagement
            topics[topic]["engaged"] += 1
    
    # Calculate rates
    results = []
    for topic, data in topics.items():
        rate = data["engaged"] / max(data["surfaces"], 1)
        results.append({
            "topic": topic,
            "surfaces": data["surfaces"],
            "engaged": data["engaged"],
            "rate": rate
        })
    
    return sorted(results, key=lambda x: -x["rate"])

def analyze_by_hour(entries):
    """Which hours get engagement?"""
    hours = defaultdict(lambda: {"surfaces": 0, "engaged": 0})
    
    for e in entries:
        hour = e.get("hourSGT")
        if hour is None:
            continue
        if e.get("type") == "surface":
            hours[hour]["surfaces"] += 1
            if e.get("gotReply"):
                hours[hour]["engaged"] += 1
    
    return dict(sorted(hours.items()))

def report(entries):
    """Generate summary report"""
    topics = analyze_by_topic(entries)
    hours = analyze_by_hour(entries)
    
    print("📊 ENGAGEMENT REPORT")
    print("=" * 40)
    
    # High engagement topics
    high = [t for t in topics if t["rate"] > 0.5 and t["surfaces"] >= 1]
    low = [t for t in topics if t["rate"] == 0 and t["surfaces"] >= 2]
    
    print("\n✅ HIGH ENGAGEMENT (>50% reply rate):")
    for t in high[:5]:
        print(f"  • {t['topic']}: {t['engaged']}/{t['surfaces']} ({t['rate']:.0%})")
    
    print("\n❌ LOW ENGAGEMENT (no replies, 2+ surfaces):")
    for t in low[:5]:
        print(f"  • {t['topic']}: {t['engaged']}/{t['surfaces']}")
    
    print("\n⏰ BEST HOURS (SGT):")
    best_hours = sorted(hours.items(), key=lambda x: -x[1].get("engaged", 0))[:3]
    for h, data in best_hours:
        if data["surfaces"] > 0:
            rate = data["engaged"] / data["surfaces"]
            print(f"  • {h}:00: {data['engaged']}/{data['surfaces']} ({rate:.0%})")
    
    print(f"\nTotal entries: {len(entries)}")

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    entries = load_feedback()
    
    if cmd == "report":
        report(entries)
    elif cmd == "topics":
        for t in analyze_by_topic(entries):
            print(f"{t['topic']}: {t['rate']:.0%} ({t['engaged']}/{t['surfaces']})")
    elif cmd == "timing":
        for h, data in sorted(analyze_by_hour(entries).items()):
            print(f"{h:02d}:00 SGT: {data}")
    else:
        print("Usage: engagement-analyzer.py [report|topics|timing]")

if __name__ == "__main__":
    main()
