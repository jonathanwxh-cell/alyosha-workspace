#!/usr/bin/env python3
"""
Reflexion Loop for Autonomous Exploration

Implements the Reflexion pattern (Shinn et al., 2023):
- Store reflections after each exploration
- Query past reflections before new explorations
- MARS: Memory → Action → Reflection → Self-improvement

Usage:
  python3 scripts/reflexion.py add          # Add reflection after exploration
  python3 scripts/reflexion.py query <topic> # Query past reflections
  python3 scripts/reflexion.py mars         # Run MARS self-assessment
  python3 scripts/reflexion.py stats        # Show reflection statistics
"""

import json
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

REFLECTIONS_FILE = Path.home() / ".openclaw/workspace/memory/reflections.jsonl"
REFLECTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_reflections():
    """Load all reflections from JSONL file."""
    reflections = []
    if REFLECTIONS_FILE.exists():
        with open(REFLECTIONS_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        reflections.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    return reflections

def add_reflection(topic: str, hypothesis: str, outcome: str, 
                   what_worked: str, what_failed: str, lesson: str,
                   confidence: str = "medium"):
    """Add a new reflection entry."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "topic": topic,
        "hypothesis": hypothesis,
        "outcome": outcome,
        "what_worked": what_worked,
        "what_failed": what_failed,
        "lesson": lesson,
        "confidence": confidence,  # low/medium/high
        "applied": False  # Whether lesson was applied to future behavior
    }
    
    with open(REFLECTIONS_FILE, 'a') as f:
        f.write(json.dumps(entry) + '\n')
    
    return entry

def query_reflections(topic: str, limit: int = 5):
    """Query reflections related to a topic (simple keyword match)."""
    reflections = load_reflections()
    topic_lower = topic.lower()
    
    # Score by relevance (simple keyword match)
    # Handles both old format (task/reflection/lesson) and new format (topic/hypothesis/lesson)
    scored = []
    for r in reflections:
        score = 0
        # Check all text fields for matches
        for field in ['topic', 'task', 'lesson', 'hypothesis', 'outcome', 'reflection', 'what_worked', 'what_failed']:
            text = r.get(field, '')
            if isinstance(text, str) and topic_lower in text.lower():
                score += 2 if field in ['topic', 'task', 'lesson'] else 1
        if score > 0:
            scored.append((score, r))
    
    # Sort by score, then recency
    scored.sort(key=lambda x: (x[0], x[1].get('timestamp', '')), reverse=True)
    return [r for _, r in scored[:limit]]

def mars_assessment():
    """
    MARS (Memory, Action, Reflection, Self-improvement) assessment.
    Analyzes reflection patterns to suggest improvements.
    """
    reflections = load_reflections()
    
    if len(reflections) < 3:
        return {
            "status": "insufficient_data",
            "message": f"Need at least 3 reflections for MARS (have {len(reflections)})",
            "suggestion": "Continue exploring and logging reflections"
        }
    
    # Analyze patterns
    total = len(reflections)
    high_conf = sum(1 for r in reflections if r.get('confidence') == 'high')
    low_conf = sum(1 for r in reflections if r.get('confidence') == 'low')
    
    # Extract common failure patterns
    failures = [r.get('what_failed', '') for r in reflections if r.get('what_failed')]
    lessons = [r.get('lesson', '') for r in reflections]
    
    # Recent trend (last 5)
    recent = reflections[-5:] if len(reflections) >= 5 else reflections
    recent_conf = [r.get('confidence', 'medium') for r in recent]
    
    return {
        "status": "ok",
        "total_reflections": total,
        "confidence_distribution": {
            "high": high_conf,
            "medium": total - high_conf - low_conf,
            "low": low_conf
        },
        "recent_trend": recent_conf,
        "top_lessons": lessons[-3:] if lessons else [],
        "improvement_suggestions": generate_suggestions(reflections)
    }

def generate_suggestions(reflections):
    """Generate self-improvement suggestions from reflection patterns."""
    suggestions = []
    
    # Check for repeated low confidence
    recent = reflections[-5:] if len(reflections) >= 5 else reflections
    low_count = sum(1 for r in recent if r.get('confidence') == 'low')
    if low_count >= 3:
        suggestions.append("Pattern: Low confidence streak. Try narrowing scope or switching topics.")
    
    # Check for unapplied lessons
    unapplied = [r for r in reflections if not r.get('applied') and r.get('confidence') == 'high']
    if len(unapplied) >= 2:
        suggestions.append(f"Pattern: {len(unapplied)} high-confidence lessons not yet applied. Review and implement.")
    
    # Check for exploration breadth
    topics = set(r.get('topic', '').lower().split()[0] for r in reflections if r.get('topic'))
    if len(topics) < 3 and len(reflections) > 5:
        suggestions.append("Pattern: Narrow topic range. Consider diversifying exploration.")
    
    if not suggestions:
        suggestions.append("No concerning patterns detected. Continue current approach.")
    
    return suggestions

def stats():
    """Show reflection statistics."""
    reflections = load_reflections()
    
    if not reflections:
        return {"total": 0, "message": "No reflections yet"}
    
    # Topic frequency - handles both old (task) and new (topic) formats
    topics = {}
    for r in reflections:
        topic = r.get('topic') or r.get('task', 'unknown')
        topics[topic] = topics.get(topic, 0) + 1
    
    # Outcome stats
    outcomes = {}
    for r in reflections:
        outcome = r.get('outcome', 'unknown')
        outcomes[outcome] = outcomes.get(outcome, 0) + 1
    
    return {
        "total": len(reflections),
        "first": reflections[0].get('timestamp', 'unknown') if reflections else None,
        "last": reflections[-1].get('timestamp', 'unknown') if reflections else None,
        "topics": dict(sorted(topics.items(), key=lambda x: -x[1])[:10]),  # Top 10
        "outcomes": outcomes,
        "confidence_summary": {
            "high": sum(1 for r in reflections if r.get('confidence') == 'high'),
            "medium": sum(1 for r in reflections if r.get('confidence') == 'medium'),
            "low": sum(1 for r in reflections if r.get('confidence') == 'low')
        }
    }

def interactive_add():
    """Interactive mode to add a reflection."""
    print("=== Add Reflection ===")
    print("(Leave blank to skip optional fields)")
    
    topic = input("Topic: ").strip()
    if not topic:
        print("Topic required.")
        return None
        
    hypothesis = input("What was your hypothesis? ").strip()
    outcome = input("What happened? ").strip()
    what_worked = input("What worked? ").strip()
    what_failed = input("What failed? ").strip()
    lesson = input("Key lesson: ").strip()
    
    confidence = input("Confidence (low/medium/high) [medium]: ").strip().lower()
    if confidence not in ['low', 'medium', 'high']:
        confidence = 'medium'
    
    entry = add_reflection(topic, hypothesis, outcome, what_worked, what_failed, lesson, confidence)
    print(f"\n✓ Reflection saved: {entry['timestamp']}")
    return entry

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'add':
        if len(sys.argv) >= 8:
            # CLI mode: topic, hypothesis, outcome, worked, failed, lesson, [confidence]
            confidence = sys.argv[8] if len(sys.argv) > 8 else 'medium'
            entry = add_reflection(sys.argv[2], sys.argv[3], sys.argv[4], 
                                   sys.argv[5], sys.argv[6], sys.argv[7], confidence)
            print(json.dumps(entry, indent=2))
        else:
            # Interactive mode
            interactive_add()
    
    elif cmd == 'query':
        if len(sys.argv) < 3:
            print("Usage: reflexion.py query <topic>")
            return
        topic = ' '.join(sys.argv[2:])
        results = query_reflections(topic)
        if results:
            print(f"=== {len(results)} reflections for '{topic}' ===\n")
            for r in results:
                ts = r.get('timestamp', 'unknown')[:10]
                title = r.get('topic') or r.get('task', 'unknown')
                print(f"[{ts}] {title}")
                # Show hypothesis or reflection (new vs old format)
                if r.get('hypothesis'):
                    print(f"  Hypothesis: {r.get('hypothesis', 'N/A')}")
                elif r.get('reflection'):
                    print(f"  Reflection: {r.get('reflection', 'N/A')[:100]}...")
                print(f"  Lesson: {r.get('lesson', 'N/A')}")
                if r.get('confidence'):
                    print(f"  Confidence: {r.get('confidence')}")
                print()
        else:
            print(f"No reflections found for '{topic}'")
    
    elif cmd == 'mars':
        result = mars_assessment()
        print(json.dumps(result, indent=2))
    
    elif cmd == 'stats':
        result = stats()
        print(json.dumps(result, indent=2))
    
    elif cmd == 'list':
        reflections = load_reflections()
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        for r in reflections[-limit:]:
            print(f"[{r['timestamp'][:10]}] {r['topic']}: {r.get('lesson', 'N/A')[:60]}")
    
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)

if __name__ == '__main__':
    main()
