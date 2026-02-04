#!/usr/bin/env python3
"""
Daemon Judge - Self-Refining Performance Evaluator
===================================================

Based on the "LLM-as-Judge" pattern from Temporal ambient agent research.
Evaluates daemon outputs and suggests prompt/behavior improvements.

This is the "judge agent" that helps the daemon self-improve:
1. Reviews recent feedback (thumbs up/down, replies)
2. Analyzes what's working vs not
3. Proposes concrete improvements

Usage:
    python3 daemon-judge.py review       # Review last 24h and score
    python3 daemon-judge.py insights     # Generate improvement insights
    python3 daemon-judge.py health       # Overall daemon health score
"""

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import Counter

WORKSPACE = Path.home() / '.openclaw/workspace'
FEEDBACK_LOG = WORKSPACE / 'memory/feedback-log.jsonl'
REFLECTIONS = WORKSPACE / 'memory/reflections.jsonl'
HEARTBEAT_STATE = WORKSPACE / 'memory/heartbeat-state.json'
TOPIC_BALANCE = WORKSPACE / 'memory/topic-balance.json'
JUDGE_LOG = WORKSPACE / 'memory/daemon-judge-log.jsonl'


def load_jsonl(path, days=7):
    """Load JSONL entries from last N days."""
    entries = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    if not path.exists():
        return entries
    
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                # Parse timestamp
                ts = entry.get('timestamp', entry.get('ts', ''))
                if ts:
                    if 'Z' in ts:
                        ts = ts.replace('Z', '+00:00')
                    dt = datetime.fromisoformat(ts)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    if dt > cutoff:
                        entries.append(entry)
            except (json.JSONDecodeError, ValueError):
                continue
    
    return entries


def load_json(path):
    """Load a JSON file."""
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def save_judge_entry(entry):
    """Save a judge log entry."""
    entry['timestamp'] = datetime.now(timezone.utc).isoformat()
    with open(JUDGE_LOG, 'a') as f:
        f.write(json.dumps(entry) + '\n')


def review_performance(days=1):
    """Review daemon performance over the last N days."""
    feedback = load_jsonl(FEEDBACK_LOG, days=days)
    reflections = load_jsonl(REFLECTIONS, days=days)
    
    print(f"🔍 Daemon Judge: Reviewing last {days} day(s)\n")
    print("=" * 50)
    
    # Feedback analysis
    positive = sum(1 for f in feedback if f.get('signal') in ('thumbs_up', 'reply', 'engaged'))
    negative = sum(1 for f in feedback if f.get('signal') in ('thumbs_down', 'negative'))
    neutral = len(feedback) - positive - negative
    
    print(f"\n📊 Feedback Signals ({len(feedback)} total)")
    print(f"   👍 Positive: {positive}")
    print(f"   👎 Negative: {negative}")
    print(f"   ➖ Neutral:  {neutral}")
    
    engagement_rate = positive / len(feedback) * 100 if feedback else 0
    print(f"   📈 Engagement rate: {engagement_rate:.0f}%")
    
    # Reflection analysis  
    successes = sum(1 for r in reflections if r.get('outcome') == 'success')
    failures = sum(1 for r in reflections if r.get('outcome') == 'failure')
    
    print(f"\n🧠 Self-Reflections ({len(reflections)} total)")
    print(f"   ✅ Successes: {successes}")
    print(f"   ❌ Failures:  {failures}")
    
    # Category distribution from feedback
    categories = Counter(f.get('category', 'unknown') for f in feedback)
    if categories:
        print(f"\n📑 Top Categories")
        for cat, count in categories.most_common(5):
            print(f"   {cat}: {count}")
    
    # Calculate overall health score (0-100)
    scores = {
        'engagement': min(engagement_rate, 100),  # Cap at 100
        'success_rate': (successes / len(reflections) * 100) if reflections else 50,
        'activity': min(len(feedback) * 10, 100)  # Activity score
    }
    health = sum(scores.values()) / len(scores)
    
    print(f"\n🏥 Health Score: {health:.0f}/100")
    print(f"   Engagement: {scores['engagement']:.0f}")
    print(f"   Success Rate: {scores['success_rate']:.0f}")
    print(f"   Activity: {scores['activity']:.0f}")
    
    return {
        'health': health,
        'engagement_rate': engagement_rate,
        'feedback_count': len(feedback),
        'positive': positive,
        'negative': negative,
        'reflections': len(reflections),
        'successes': successes,
        'failures': failures
    }


def generate_insights():
    """Generate improvement insights based on patterns."""
    feedback = load_jsonl(FEEDBACK_LOG, days=7)
    reflections = load_jsonl(REFLECTIONS, days=7)
    
    print("💡 Daemon Judge: Generating Insights\n")
    print("=" * 50)
    
    insights = []
    
    # Pattern 1: What categories get engagement?
    engaged_cats = Counter()
    ignored_cats = Counter()
    for f in feedback:
        cat = f.get('category', 'unknown')
        if f.get('signal') in ('thumbs_up', 'reply', 'engaged'):
            engaged_cats[cat] += 1
        elif f.get('signal') in ('ignored', 'no_reply'):
            ignored_cats[cat] += 1
    
    if engaged_cats:
        top_engaged = engaged_cats.most_common(3)
        print("\n✅ High-Engagement Categories:")
        for cat, count in top_engaged:
            print(f"   → {cat} ({count} positive signals)")
        insights.append(f"INCREASE: {', '.join(c for c, _ in top_engaged[:2])}")
    
    if ignored_cats:
        top_ignored = ignored_cats.most_common(3)
        print("\n⚠️ Low-Engagement Categories:")
        for cat, count in top_ignored:
            print(f"   → {cat} ({count} ignored)")
        insights.append(f"REDUCE: {', '.join(c for c, _ in top_ignored[:2])}")
    
    # Pattern 2: Recurring failure lessons
    failure_lessons = [r.get('lesson', '') for r in reflections 
                       if r.get('outcome') == 'failure' and r.get('lesson')]
    if failure_lessons:
        print("\n❌ Recurring Failure Patterns:")
        # Simple keyword extraction
        words = ' '.join(failure_lessons).lower()
        if 'permission' in words or 'ask' in words:
            print("   → Still asking permission too often")
            insights.append("AVOID: Asking permission for autonomous actions")
        if 'long' in words or 'verbose' in words:
            print("   → Outputs too long/verbose")
            insights.append("AVOID: Over-verbose outputs")
        if 'finance' in words or 'market' in words:
            print("   → Over-focusing on finance")
            insights.append("AVOID: Finance over-representation")
    
    # Pattern 3: Success procedures
    success_lessons = [r.get('lesson', '') for r in reflections 
                       if r.get('outcome') == 'success' and r.get('lesson')]
    if success_lessons:
        print("\n✅ Working Procedures (replicate these):")
        for lesson in success_lessons[:3]:
            print(f"   → {lesson[:70]}")
    
    # Recommendations
    print("\n🎯 RECOMMENDATIONS:")
    for i, insight in enumerate(insights, 1):
        print(f"   {i}. {insight}")
    
    # Save insights
    save_judge_entry({
        'action': 'insights',
        'engaged_cats': dict(engaged_cats.most_common(5)),
        'ignored_cats': dict(ignored_cats.most_common(5)),
        'insights': insights
    })
    
    return insights


def health_check():
    """Quick daemon health check with action items."""
    stats = review_performance(days=1)
    
    print("\n" + "=" * 50)
    print("🩺 DIAGNOSIS:\n")
    
    actions = []
    
    # Health thresholds
    if stats['health'] < 50:
        print("⚠️  HEALTH CRITICAL: Major improvement needed")
        actions.append("Review HEARTBEAT.md for issues")
    elif stats['health'] < 70:
        print("🟡 HEALTH MODERATE: Some optimization possible")
    else:
        print("✅ HEALTH GOOD: Daemon performing well")
    
    if stats['engagement_rate'] < 30:
        print("📉 Low engagement - consider surfacing more relevant content")
        actions.append("Increase relevance of surfaces")
    
    if stats['negative'] > stats['positive']:
        print("👎 More negative than positive signals")
        actions.append("Review what's being downvoted")
    
    if stats['failures'] > stats['successes'] and stats['reflections'] > 3:
        print("❌ More failures than successes in reflections")
        actions.append("Review failure patterns with: reflexion.py failures")
    
    if actions:
        print("\n📋 ACTION ITEMS:")
        for action in actions:
            print(f"   • {action}")
    
    save_judge_entry({
        'action': 'health_check',
        'stats': stats,
        'actions': actions
    })
    
    return stats['health']


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'review':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        review_performance(days)
    
    elif cmd == 'insights':
        generate_insights()
    
    elif cmd == 'health':
        health_check()
    
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
