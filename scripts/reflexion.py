#!/usr/bin/env python3
"""
Reflexion System
================

Verbal reinforcement learning for the daemon. 
Based on Shinn et al. (2023) "Reflexion: Language Agents with Verbal Reinforcement Learning"

Components:
- Memory: Episodic memory of past task attempts + reflections
- Query: Semantic search over past reflections before new tasks  
- Reflect: Generate structured reflection after task completion
- Score: Self-evaluate task outcomes

Usage:
    python3 reflexion.py query "research topic"     # Find relevant past reflections
    python3 reflexion.py add                        # Interactive: add new reflection
    python3 reflexion.py stats                      # Show reflection statistics
    python3 reflexion.py lessons                    # Extract top lessons learned
    python3 reflexion.py recent [n]                 # Show last N reflections (default 5)
    python3 reflexion.py failures                   # Show only failures (best for learning)

The daemon should:
1. BEFORE task: query past reflections for similar tasks
2. DURING task: apply lessons learned
3. AFTER task: add reflection with outcome + lesson
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from collections import Counter

REFLECTIONS_FILE = Path.home() / '.openclaw/workspace/memory/reflections.jsonl'

# Keywords for semantic matching (simple but effective)
CATEGORY_KEYWORDS = {
    'research': ['research', 'search', 'find', 'discover', 'explore', 'investigate', 'scan'],
    'analysis': ['analyze', 'analysis', 'evaluate', 'assess', 'compare', 'review'],
    'writing': ['write', 'draft', 'compose', 'create', 'document', 'article'],
    'coding': ['code', 'script', 'build', 'implement', 'fix', 'debug', 'program'],
    'communication': ['send', 'message', 'notify', 'alert', 'surface', 'share'],
    'planning': ['plan', 'schedule', 'organize', 'prioritize', 'strategy'],
}


def load_reflections():
    """Load all reflections from JSONL file."""
    reflections = []
    if not REFLECTIONS_FILE.exists():
        return reflections
    
    with open(REFLECTIONS_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    reflections.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return reflections


def save_reflection(reflection):
    """Append a new reflection to the file."""
    with open(REFLECTIONS_FILE, 'a') as f:
        f.write(json.dumps(reflection) + '\n')


def get_category(text):
    """Determine category from text using keyword matching."""
    text_lower = text.lower()
    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        scores[cat] = sum(1 for kw in keywords if kw in text_lower)
    
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else 'general'


def query_reflections(query, limit=5):
    """Find relevant past reflections for a query."""
    reflections = load_reflections()
    if not reflections:
        print("📭 No reflections yet. Start learning!")
        return []
    
    query_lower = query.lower()
    query_words = set(query_lower.split())
    query_category = get_category(query)
    
    scored = []
    for r in reflections:
        score = 0
        
        # Match on task description
        task = r.get('task', '').lower()
        task_words = set(task.split())
        word_overlap = len(query_words & task_words)
        score += word_overlap * 2
        
        # Match on category
        if get_category(task) == query_category:
            score += 3
        
        # Match on lesson content
        lesson = r.get('lesson', '').lower()
        if any(w in lesson for w in query_words):
            score += 2
        
        # Boost successful outcomes
        if r.get('outcome') == 'success':
            score += 1
        
        # Recency bonus (last 30 days)
        try:
            ts = datetime.fromisoformat(r.get('timestamp', ''))
            days_ago = (datetime.now() - ts).days
            if days_ago < 30:
                score += 1
        except:
            pass
        
        if score > 0:
            scored.append((score, r))
    
    # Sort by score descending
    scored.sort(key=lambda x: -x[0])
    
    results = [r for _, r in scored[:limit]]
    
    if results:
        print(f"🔍 Found {len(results)} relevant reflection(s) for: {query}\n")
        for i, r in enumerate(results, 1):
            outcome_emoji = {'success': '✅', 'partial': '🟡', 'failure': '❌'}.get(r.get('outcome'), '❓')
            print(f"{i}. {outcome_emoji} {r.get('task', 'Unknown task')[:60]}")
            print(f"   💡 Lesson: {r.get('lesson', 'None')[:80]}")
            print()
    else:
        print(f"📭 No relevant reflections for: {query}")
    
    return results


def add_reflection_interactive():
    """Interactively add a new reflection."""
    print("📝 New Reflection\n")
    
    task = input("Task (what did you try to do?): ").strip()
    if not task:
        print("❌ Task required")
        return
    
    outcome = input("Outcome (success/partial/failure): ").strip().lower()
    if outcome not in ['success', 'partial', 'failure']:
        outcome = 'partial'
    
    reflection = input("Reflection (what happened?): ").strip()
    lesson = input("Lesson (what to remember?): ").strip()
    would_repeat = input("Would repeat approach? (y/n): ").strip().lower() == 'y'
    
    entry = {
        'timestamp': datetime.now().isoformat(),
        'task': task,
        'outcome': outcome,
        'reflection': reflection,
        'lesson': lesson,
        'would_repeat': would_repeat,
        'category': get_category(task)
    }
    
    save_reflection(entry)
    print(f"\n✅ Reflection saved to {REFLECTIONS_FILE.name}")


def add_reflection_direct(task, outcome, reflection, lesson, would_repeat=True):
    """Add reflection programmatically (for daemon use)."""
    entry = {
        'timestamp': datetime.now().isoformat(),
        'task': task,
        'outcome': outcome,
        'reflection': reflection,
        'lesson': lesson,
        'would_repeat': would_repeat,
        'category': get_category(task)
    }
    save_reflection(entry)
    return entry


def show_stats():
    """Show reflection statistics."""
    reflections = load_reflections()
    
    if not reflections:
        print("📭 No reflections yet")
        return
    
    outcomes = Counter(r.get('outcome', 'unknown') for r in reflections)
    categories = Counter(r.get('category', 'general') for r in reflections)
    
    total = len(reflections)
    success_rate = outcomes.get('success', 0) / total * 100 if total > 0 else 0
    
    print(f"📊 Reflection Stats ({total} total)\n")
    print(f"Success rate: {success_rate:.0f}%")
    print(f"  ✅ Success: {outcomes.get('success', 0)}")
    print(f"  🟡 Partial: {outcomes.get('partial', 0)}")
    print(f"  ❌ Failure: {outcomes.get('failure', 0)}")
    print(f"\nBy category:")
    for cat, count in categories.most_common():
        print(f"  {cat}: {count}")


def extract_lessons():
    """Extract and display top lessons learned."""
    reflections = load_reflections()
    
    if not reflections:
        print("📭 No reflections yet")
        return
    
    # Get successful lessons
    lessons = [(r.get('lesson', ''), r.get('task', ''), r.get('outcome', ''))
               for r in reflections if r.get('lesson')]
    
    print(f"📚 Top Lessons Learned ({len(lessons)} total)\n")
    
    # Group by category
    by_category = {}
    for r in reflections:
        if r.get('lesson'):
            cat = r.get('category', 'general')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(r)
    
    for cat, items in sorted(by_category.items()):
        print(f"**{cat.upper()}**")
        # Show most recent 3 per category
        for r in sorted(items, key=lambda x: x.get('timestamp', ''), reverse=True)[:3]:
            outcome_emoji = {'success': '✅', 'partial': '🟡', 'failure': '❌'}.get(r.get('outcome'), '❓')
            print(f"  {outcome_emoji} {r.get('lesson', '')[:70]}")
        print()


def show_recent(n=5):
    """Show the most recent N reflections."""
    reflections = load_reflections()
    
    if not reflections:
        print("📭 No reflections yet")
        return
    
    # Sort by timestamp descending
    sorted_refs = sorted(reflections, 
                         key=lambda x: x.get('timestamp', ''), 
                         reverse=True)[:n]
    
    print(f"🕐 Last {len(sorted_refs)} Reflections\n")
    
    for r in sorted_refs:
        outcome_emoji = {'success': '✅', 'partial': '🟡', 'failure': '❌'}.get(r.get('outcome'), '❓')
        ts = r.get('timestamp', '')[:16].replace('T', ' ')  # Trim to minute
        cat = r.get('category', 'general')
        
        print(f"{outcome_emoji} [{ts}] ({cat})")
        print(f"   Task: {r.get('task', 'Unknown')[:65]}")
        if r.get('lesson'):
            print(f"   💡 {r.get('lesson', '')[:70]}")
        print()


def show_failures():
    """Show only failures - most valuable for learning."""
    reflections = load_reflections()
    
    if not reflections:
        print("📭 No reflections yet")
        return
    
    failures = [r for r in reflections if r.get('outcome') in ('failure', 'partial')]
    
    if not failures:
        print("🎉 No failures recorded! (Suspicious...)")
        return
    
    # Sort by timestamp descending
    failures = sorted(failures, 
                      key=lambda x: x.get('timestamp', ''), 
                      reverse=True)
    
    print(f"❌ Failures & Partial Outcomes ({len(failures)} total)\n")
    print("These are your best teachers:\n")
    
    for r in failures:
        outcome_emoji = {'partial': '🟡', 'failure': '❌'}.get(r.get('outcome'), '❓')
        ts = r.get('timestamp', '')[:10]  # Just date
        
        print(f"{outcome_emoji} [{ts}] {r.get('task', 'Unknown')[:55]}")
        if r.get('reflection'):
            print(f"   What happened: {r.get('reflection', '')[:65]}")
        if r.get('lesson'):
            print(f"   💡 Lesson: {r.get('lesson', '')[:65]}")
        print()
    
    # Summary of recurring patterns
    lesson_words = ' '.join(r.get('lesson', '') for r in failures).lower()
    recurring = []
    if lesson_words.count('permission') >= 2 or lesson_words.count('asking') >= 2:
        recurring.append("🔁 Permission-asking (recurring)")
    if lesson_words.count('curation') >= 2 or lesson_words.count('analysis') >= 2:
        recurring.append("🔁 Curation without analysis (recurring)")
    
    if recurring:
        print("⚠️  Recurring Patterns Detected:")
        for pattern in recurring:
            print(f"   {pattern}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'query' and len(sys.argv) >= 3:
        query = ' '.join(sys.argv[2:])
        query_reflections(query)
    
    elif cmd == 'add':
        if len(sys.argv) >= 6:
            # Direct add: reflexion.py add "task" "outcome" "reflection" "lesson"
            add_reflection_direct(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
            print("✅ Reflection added")
        else:
            add_reflection_interactive()
    
    elif cmd == 'stats':
        show_stats()
    
    elif cmd == 'lessons':
        extract_lessons()
    
    elif cmd == 'recent':
        n = int(sys.argv[2]) if len(sys.argv) >= 3 else 5
        show_recent(n)
    
    elif cmd == 'failures':
        show_failures()
    
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
