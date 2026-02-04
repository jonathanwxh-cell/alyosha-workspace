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
    python3 reflexion.py export                     # Export lessons as markdown for MEMORY.md
    python3 reflexion.py trends                     # Show success rate trends over time
    
    # MARS Framework commands (Metacognitive Agent Reflective Self-improvement)
    python3 reflexion.py avoid [n]                  # Principle-based lessons: what NOT to do
    python3 reflexion.py procedures [n]             # Procedural lessons: what TO do
    python3 reflexion.py mars                       # Combined MARS view (both types)

The daemon should:
1. BEFORE task: query past reflections for similar tasks
2. DURING task: apply lessons learned
3. AFTER task: add reflection with outcome + lesson
"""

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import Counter

REFLECTIONS_FILE = Path.home() / '.openclaw/workspace/memory/reflections.jsonl'

# Keywords for semantic matching (expanded for better categorization)
CATEGORY_KEYWORDS = {
    'research': ['research', 'search', 'find', 'discover', 'explore', 'investigate', 'scan', 
                 'paper', 'arxiv', 'study', 'source', 'fetch', 'web_search', 'news'],
    'analysis': ['analyze', 'analysis', 'evaluate', 'assess', 'compare', 'review', 'deep',
                 'synthesis', 'insight', 'framework', 'thesis', 'investment', 'stock', 'market'],
    'writing': ['write', 'draft', 'compose', 'create', 'document', 'article', 'post',
                'substack', 'blog', 'content', 'summary', 'brief'],
    'coding': ['code', 'script', 'build', 'implement', 'fix', 'debug', 'program', 'python',
               'tool', 'cron', 'automat', 'function', 'class', 'api'],
    'communication': ['send', 'message', 'notify', 'alert', 'surface', 'share', 'telegram',
                      'email', 'reply', 'respond', 'deliver'],
    'planning': ['plan', 'schedule', 'organize', 'prioritize', 'strategy', 'goal', 'project'],
    'meta': ['daemon', 'heartbeat', 'improve', 'evolve', 'self', 'reflexion', 'memory',
             'pattern', 'lesson', 'learn', 'metacognitive', 'autonomous'],
    'creative': ['creative', 'art', 'image', 'visual', 'story', 'fiction', 'sonif', 
                 'generate', 'dall-e', 'aesthetic'],
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


def get_category(text, additional_text=''):
    """Determine category from text using keyword matching.
    
    Args:
        text: Primary text (task description)
        additional_text: Secondary text (lesson, reflection) for better matching
    """
    combined = f"{text} {additional_text}".lower()
    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        # Count keyword matches, with partial matching
        score = 0
        for kw in keywords:
            if kw in combined:
                score += 2 if kw in text.lower() else 1  # Task matches worth more
        scores[cat] = score
    
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
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'task': task,
        'outcome': outcome,
        'reflection': reflection,
        'lesson': lesson,
        'would_repeat': would_repeat,
        'category': get_category(task, f"{reflection} {lesson}")
    }
    
    save_reflection(entry)
    print(f"\n✅ Reflection saved to {REFLECTIONS_FILE.name}")


def add_reflection_direct(task, outcome, reflection, lesson, would_repeat=True, lesson_type=None):
    """Add reflection programmatically (for daemon use).
    
    Args:
        task: What was attempted
        outcome: 'success', 'partial', or 'failure'
        reflection: What happened
        lesson: What to remember
        would_repeat: Whether approach should be repeated
        lesson_type: 'avoid' (principle-based) or 'procedure' (success strategy)
                     If None, auto-detected from outcome
    
    Based on MARS framework (NTU Singapore 2026):
    - Principle-based learning: Rules to AVOID errors
    - Procedural learning: Steps to REPLICATE success
    """
    # Auto-detect lesson type if not provided
    if lesson_type is None:
        if outcome == 'failure' or not would_repeat:
            lesson_type = 'avoid'  # Principle-based: what NOT to do
        else:
            lesson_type = 'procedure'  # Procedural: what TO do
    
    entry = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'task': task,
        'outcome': outcome,
        'reflection': reflection,
        'lesson': lesson,
        'would_repeat': would_repeat,
        'lesson_type': lesson_type,  # NEW: 'avoid' or 'procedure'
        'category': get_category(task, f"{reflection} {lesson}")
    }
    save_reflection(entry)
    return entry


def query_by_type(lesson_type, limit=10):
    """Query reflections by lesson type (avoid or procedure).
    
    Based on MARS framework - separate what-to-avoid from what-works.
    """
    reflections = load_reflections()
    
    # Filter by type (with backwards compatibility)
    typed = []
    for r in reflections:
        r_type = r.get('lesson_type')
        if r_type is None:
            # Infer type for old entries
            if r.get('outcome') == 'failure' or not r.get('would_repeat', True):
                r_type = 'avoid'
            else:
                r_type = 'procedure'
        
        if r_type == lesson_type and r.get('lesson'):
            typed.append(r)
    
    # Sort by recency
    typed = sorted(typed, key=lambda x: x.get('timestamp', ''), reverse=True)[:limit]
    
    type_emoji = '🚫' if lesson_type == 'avoid' else '✅'
    type_label = 'AVOID (principle-based)' if lesson_type == 'avoid' else 'PROCEDURE (success strategies)'
    
    print(f"{type_emoji} {type_label} ({len(typed)} lessons)\n")
    
    for r in typed:
        cat = r.get('category', 'general')
        print(f"  [{cat}] {r.get('lesson', '')[:75]}")
    
    return typed


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


def export_for_memory():
    """Export lessons in markdown format suitable for MEMORY.md updates."""
    reflections = load_reflections()
    
    if not reflections:
        print("📭 No reflections yet")
        return
    
    # Get last 30 days of reflections
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    recent = []
    for r in reflections:
        try:
            ts = r.get('timestamp', '')
            if 'Z' in ts:
                ts = ts.replace('Z', '+00:00')
            elif '+' not in ts and len(ts) == 19:
                ts = ts + '+00:00'
            dt = datetime.fromisoformat(ts)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            if dt > cutoff:
                recent.append(r)
        except:
            recent.append(r)  # Include if date parsing fails
    
    # Group by outcome
    successes = [r for r in recent if r.get('outcome') == 'success' and r.get('lesson')]
    failures = [r for r in recent if r.get('outcome') in ('failure', 'partial') and r.get('lesson')]
    
    # Generate markdown
    print("## Lessons Learned (from reflections.jsonl)\n")
    print(f"*Exported: {datetime.now(timezone.utc).strftime('%Y-%m-%d')} | "
          f"Period: Last 30 days | Total: {len(recent)} reflections*\n")
    
    if successes:
        print("### What Worked\n")
        seen_lessons = set()
        for r in sorted(successes, key=lambda x: x.get('timestamp', ''), reverse=True):
            lesson = r.get('lesson', '')[:100]
            # Dedupe similar lessons
            lesson_key = lesson[:30].lower()
            if lesson_key not in seen_lessons:
                seen_lessons.add(lesson_key)
                print(f"- {lesson}")
        print()
    
    if failures:
        print("### What Didn't Work (Learn From These)\n")
        seen_lessons = set()
        for r in sorted(failures, key=lambda x: x.get('timestamp', ''), reverse=True):
            lesson = r.get('lesson', '')[:100]
            lesson_key = lesson[:30].lower()
            if lesson_key not in seen_lessons:
                seen_lessons.add(lesson_key)
                outcome_marker = "⚠️" if r.get('outcome') == 'partial' else "❌"
                print(f"- {outcome_marker} {lesson}")
        print()
    
    # Stats summary
    total = len(recent)
    success_count = len([r for r in recent if r.get('outcome') == 'success'])
    print(f"### Stats\n")
    print(f"- Success rate: {success_count/total*100:.0f}% ({success_count}/{total})")
    
    # Category breakdown
    cats = Counter(r.get('category', 'general') for r in recent)
    print(f"- Top categories: {', '.join(f'{c}({n})' for c, n in cats.most_common(3))}")
    
    print("\n---")
    print("*Copy relevant lessons to MEMORY.md → Lessons Learned section*")


def show_trends():
    """Show success rate trends over time."""
    reflections = load_reflections()
    
    if len(reflections) < 5:
        print("📭 Need more reflections for trend analysis (min 5)")
        return
    
    # Group by week
    weeks = {}
    for r in reflections:
        try:
            ts = r.get('timestamp', '')[:10]
            dt = datetime.fromisoformat(ts)
            week = dt.strftime('%Y-W%W')
            if week not in weeks:
                weeks[week] = {'success': 0, 'partial': 0, 'failure': 0, 'total': 0}
            outcome = r.get('outcome', 'partial')
            weeks[week][outcome] = weeks[week].get(outcome, 0) + 1
            weeks[week]['total'] += 1
        except:
            pass
    
    print("📈 Success Rate Trends by Week\n")
    
    for week in sorted(weeks.keys())[-8:]:  # Last 8 weeks
        stats = weeks[week]
        total = stats['total']
        rate = stats['success'] / total * 100 if total > 0 else 0
        bar = "█" * int(rate / 10)
        print(f"   {week}: {bar:10} {rate:5.0f}% ({stats['success']}/{total})")
    
    # Overall trend
    sorted_weeks = sorted(weeks.keys())
    if len(sorted_weeks) >= 2:
        first_half = sorted_weeks[:len(sorted_weeks)//2]
        second_half = sorted_weeks[len(sorted_weeks)//2:]
        
        first_rate = sum(weeks[w]['success'] for w in first_half) / sum(weeks[w]['total'] for w in first_half) * 100
        second_rate = sum(weeks[w]['success'] for w in second_half) / sum(weeks[w]['total'] for w in second_half) * 100
        
        trend = "📈 Improving" if second_rate > first_rate + 5 else "📉 Declining" if second_rate < first_rate - 5 else "➡️ Stable"
        print(f"\n{trend}: {first_rate:.0f}% → {second_rate:.0f}%")


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
    
    elif cmd == 'export':
        export_for_memory()
    
    elif cmd == 'trends':
        show_trends()
    
    elif cmd == 'avoid':
        # Show principle-based lessons (what NOT to do)
        n = int(sys.argv[2]) if len(sys.argv) >= 3 else 10
        query_by_type('avoid', n)
    
    elif cmd == 'procedures' or cmd == 'procedure':
        # Show procedural lessons (what TO do)
        n = int(sys.argv[2]) if len(sys.argv) >= 3 else 10
        query_by_type('procedure', n)
    
    elif cmd == 'mars':
        # Show both types side by side (MARS framework view)
        print("🧠 MARS Framework View: Metacognitive Reflections\n")
        print("=" * 60)
        query_by_type('avoid', 5)
        print()
        query_by_type('procedure', 5)
        print("\nTip: Before tasks, check 'avoid' to prevent errors,")
        print("     then 'procedures' to replicate success.")
    
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
