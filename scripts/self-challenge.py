#!/usr/bin/env python3
"""
Self-Challenge Generator
Generates practice tasks based on identified weaknesses

Reads from reflections.jsonl to find failure patterns,
then generates targeted practice tasks.

Usage:
  python3 self-challenge.py           # Generate a challenge
  python3 self-challenge.py --list    # List recent weaknesses
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

WORKSPACE = Path(__file__).parent.parent
REFLECTIONS_FILE = WORKSPACE / "memory" / "reflections.jsonl"

# Challenge templates based on weakness categories
CHALLENGE_TEMPLATES = {
    "curation": [
        "Find ONE paper on {topic}. Read it fully. Write a 500-word synthesis with: key argument, methodology, limitations, and your assessment.",
        "Find 3 articles on {topic}. For each: state the non-obvious insight, rate source credibility (1-5), identify what they get wrong.",
        "Curate a single recommendation for Jon on {topic}. Follow protocols/curation-protocol.md exactly. Self-score before outputting."
    ],
    "depth": [
        "Pick any topic Jon discussed this week. Go 3 levels deeper than surface analysis. Produce a structured deep dive.",
        "Take your last research output. Identify the weakest section. Rewrite it with 2x the depth.",
        "Find a contrarian view on {topic}. Steel-man it. Then respond to it."
    ],
    "action": [
        "Identify one infrastructure gap in the workspace. Fix it without asking. Document what you did.",
        "Review the last 5 interactions. For each 'Want me to...?' find what you should have just done.",
        "Pick a stale tracking file. Either update it or delete it. Don't leave it."
    ],
    "memory": [
        "Read MEMORY.md fully. Identify 3 lessons you've violated in the last week. Log each violation.",
        "Review memory/reflections.jsonl. Find a lesson that repeats. Create a protocol to prevent it.",
        "Distill today's daily log into 3 bullet points for MEMORY.md. Actually add them."
    ],
    "analysis": [
        "Take any recent recommendation. Apply Taleb's fragility framework to it. What's the tail risk?",
        "Find a consensus view on {topic}. List 3 reasons it might be wrong.",
        "Take a recent output. Score it on: relevance, depth, originality, actionability. Be harsh."
    ]
}

def load_reflections(days: int = 14) -> list:
    """Load recent reflections"""
    if not REFLECTIONS_FILE.exists():
        return []
    
    cutoff = datetime.now() - timedelta(days=days)
    reflections = []
    
    with open(REFLECTIONS_FILE) as f:
        for line in f:
            try:
                r = json.loads(line.strip())
                if r.get("timestamp"):
                    ts = datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00"))
                    if ts.replace(tzinfo=None) > cutoff:
                        reflections.append(r)
            except:
                continue
    
    return reflections

def identify_weaknesses(reflections: list) -> dict:
    """Identify weakness categories from reflections"""
    weakness_keywords = {
        "curation": ["curation", "recommend", "surface", "read", "content"],
        "depth": ["depth", "surface-level", "shallow", "more detail"],
        "action": ["permission", "ask", "should have", "could have"],
        "memory": ["memory", "forgot", "remember", "lesson", "repeat"],
        "analysis": ["analysis", "insight", "obvious", "generic"]
    }
    
    weakness_counts = Counter()
    
    for r in reflections:
        outcome = r.get("outcome", "")
        lesson = r.get("lesson", "").lower()
        reflection = r.get("reflection", "").lower()
        combined = f"{lesson} {reflection}"
        
        if outcome in ["failure", "partial"]:
            for category, keywords in weakness_keywords.items():
                if any(kw in combined for kw in keywords):
                    weakness_counts[category] += 1
    
    return dict(weakness_counts)

def generate_challenge(weakness_category: str, topic: str = "AI") -> str:
    """Generate a challenge for a weakness category"""
    import random
    
    templates = CHALLENGE_TEMPLATES.get(weakness_category, CHALLENGE_TEMPLATES["depth"])
    template = random.choice(templates)
    
    return template.format(topic=topic)

def get_recent_topics() -> list:
    """Get topics from recent daily logs"""
    topics = ["AI infrastructure", "consciousness", "NVIDIA", "market fragility", "geopolitics"]
    
    # Could enhance by parsing recent logs
    return topics

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        reflections = load_reflections()
        weaknesses = identify_weaknesses(reflections)
        
        print("Identified weaknesses (last 14 days):")
        for category, count in sorted(weaknesses.items(), key=lambda x: -x[1]):
            print(f"  {category}: {count} occurrences")
        return
    
    reflections = load_reflections()
    weaknesses = identify_weaknesses(reflections)
    
    if not weaknesses:
        print("No weaknesses identified from recent reflections.")
        print("Generating random skill-building challenge...")
        import random
        category = random.choice(list(CHALLENGE_TEMPLATES.keys()))
    else:
        # Pick the most common weakness
        category = max(weaknesses, key=weaknesses.get)
    
    topics = get_recent_topics()
    import random
    topic = random.choice(topics)
    
    challenge = generate_challenge(category, topic)
    
    print(f"🎯 SELF-CHALLENGE")
    print(f"Category: {category}")
    print(f"Challenge: {challenge}")
    print()
    print("Complete this challenge, then log the outcome to reflections.jsonl")

if __name__ == "__main__":
    main()
