#!/usr/bin/env python3
"""
Self-Improvement Engine
========================

Analyzes feedback and reflections to propose instruction updates.

Patterns detected:
1. Repeated lessons (same insight 2+ times) → consolidate into MEMORY.md
2. Explicit instructions from Jon → extract rules
3. Low-engagement crons → propose disabling
4. Successful patterns → reinforce

Usage:
    python3 self-improve.py analyze     # Show proposed improvements
    python3 self-improve.py apply       # Apply improvements automatically
    python3 self-improve.py --dry-run   # Show what would change
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict

WORKSPACE = Path.home() / '.openclaw/workspace'
REFLECTIONS = WORKSPACE / 'memory/reflections.jsonl'
FEEDBACK = WORKSPACE / 'memory/feedback-log.jsonl'
MEMORY = WORKSPACE / 'MEMORY.md'
SELF_IMPROVE_LOG = WORKSPACE / 'memory/self-improvement-log.md'


def load_jsonl(path):
    """Load JSONL file."""
    entries = []
    if path.exists():
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except:
                        pass
    return entries


def extract_lesson_patterns(reflections):
    """Find repeated lessons that should be consolidated."""
    lessons = [r.get('lesson', '') for r in reflections if r.get('lesson')]
    
    # Simple keyword extraction for pattern matching
    keywords = defaultdict(list)
    for lesson in lessons:
        words = set(re.findall(r'\b\w{4,}\b', lesson.lower()))
        for word in words:
            if word not in {'that', 'this', 'with', 'from', 'have', 'been', 'will', 'would', 'could', 'should'}:
                keywords[word].append(lesson)
    
    # Find keywords appearing in multiple lessons
    patterns = []
    for word, matching_lessons in keywords.items():
        if len(matching_lessons) >= 2:
            patterns.append({
                'keyword': word,
                'count': len(matching_lessons),
                'lessons': matching_lessons[:3]  # Sample
            })
    
    return sorted(patterns, key=lambda x: -x['count'])[:5]


def extract_explicit_instructions(feedback):
    """Find explicit instructions from Jon."""
    instructions = []
    for entry in feedback:
        if entry.get('type') == 'instruction':
            instructions.append({
                'content': entry.get('content', ''),
                'lesson': entry.get('lesson', ''),
                'timestamp': entry.get('timestamp', '')
            })
    return instructions


def check_memory_for_lesson(lesson_text):
    """Check if a lesson is already in MEMORY.md."""
    if not MEMORY.exists():
        return False
    content = MEMORY.read_text().lower()
    # Check for key phrases
    key_words = [w for w in lesson_text.lower().split() if len(w) > 4][:3]
    matches = sum(1 for w in key_words if w in content)
    return matches >= 2  # If 2+ key words match, probably already there


def propose_improvements(reflections, feedback):
    """Generate proposed improvements."""
    proposals = []
    
    # 1. Check for repeated lesson patterns
    patterns = extract_lesson_patterns(reflections)
    for p in patterns:
        if p['count'] >= 2:
            sample_lesson = p['lessons'][0]
            if not check_memory_for_lesson(sample_lesson):
                proposals.append({
                    'type': 'consolidate_lesson',
                    'reason': f"Lesson pattern '{p['keyword']}' appears {p['count']} times",
                    'content': sample_lesson,
                    'action': 'Add to MEMORY.md'
                })
    
    # 2. Check for explicit instructions not yet codified
    instructions = extract_explicit_instructions(feedback)
    for inst in instructions[-5:]:  # Last 5
        lesson = inst.get('lesson', '')
        if lesson and not check_memory_for_lesson(lesson):
            proposals.append({
                'type': 'codify_instruction',
                'reason': f"Explicit instruction from Jon",
                'content': lesson,
                'action': 'Add to MEMORY.md'
            })
    
    # 3. Check reflection success rate by category
    categories = defaultdict(lambda: {'success': 0, 'total': 0})
    for r in reflections:
        cat = r.get('category', 'uncategorized')
        categories[cat]['total'] += 1
        if r.get('outcome') == 'success':
            categories[cat]['success'] += 1
    
    for cat, stats in categories.items():
        if stats['total'] >= 3:
            rate = stats['success'] / stats['total']
            if rate < 0.5:
                proposals.append({
                    'type': 'review_category',
                    'reason': f"Category '{cat}' has {rate:.0%} success rate",
                    'content': f"Review approach for {cat} tasks",
                    'action': 'Investigate'
                })
    
    return proposals


def get_next_lesson_number():
    """Get next lesson number from MEMORY.md."""
    if not MEMORY.exists():
        return 1
    content = MEMORY.read_text()
    numbers = re.findall(r'^(\d+)\.\s+\*\*', content, re.MULTILINE)
    if numbers:
        return max(int(n) for n in numbers) + 1
    return 1


def apply_improvement(proposal, dry_run=False):
    """Apply a single improvement."""
    if proposal['type'] in ('consolidate_lesson', 'codify_instruction'):
        if dry_run:
            return f"Would add to MEMORY.md: {proposal['content'][:50]}..."
        
        # Add to MEMORY.md
        lesson_num = get_next_lesson_number()
        new_lesson = f"{lesson_num}. **{proposal['content'][:100]}**"
        
        content = MEMORY.read_text()
        # Find the lessons section and append
        if '## Lessons Learned' in content:
            # Add after last numbered lesson
            lines = content.split('\n')
            insert_idx = None
            for i, line in enumerate(lines):
                if re.match(r'^\d+\.\s+\*\*', line):
                    insert_idx = i + 1
            
            if insert_idx:
                lines.insert(insert_idx, new_lesson)
                MEMORY.write_text('\n'.join(lines))
                return f"Added lesson #{lesson_num}"
        
        return "Could not find insertion point"
    
    return f"No action for type: {proposal['type']}"


def log_improvement(proposal, result):
    """Log improvement to self-improvement-log.md."""
    timestamp = datetime.now().isoformat()
    entry = f"""
## {timestamp[:10]} — Auto-improvement

**Type:** {proposal['type']}
**Reason:** {proposal['reason']}
**Action:** {result}
**Content:** {proposal['content'][:100]}...

---
"""
    with open(SELF_IMPROVE_LOG, 'a') as f:
        f.write(entry)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 self-improve.py [analyze|apply|--dry-run]")
        return
    
    action = sys.argv[1]
    dry_run = action == '--dry-run'
    
    reflections = load_jsonl(REFLECTIONS)
    feedback = load_jsonl(FEEDBACK)
    
    print(f"📊 Self-Improvement Analysis")
    print(f"   Reflections: {len(reflections)}")
    print(f"   Feedback entries: {len(feedback)}")
    print()
    
    proposals = propose_improvements(reflections, feedback)
    
    if not proposals:
        print("✅ No improvements proposed. System is well-calibrated.")
        return
    
    print(f"📝 Proposed Improvements ({len(proposals)}):\n")
    
    for i, p in enumerate(proposals, 1):
        print(f"{i}. [{p['type']}] {p['reason']}")
        print(f"   Content: {p['content'][:60]}...")
        print(f"   Action: {p['action']}")
        print()
    
    if action == 'apply' and not dry_run:
        print("🔧 Applying improvements...\n")
        for p in proposals:
            if p['type'] in ('consolidate_lesson', 'codify_instruction'):
                result = apply_improvement(p)
                log_improvement(p, result)
                print(f"   ✅ {result}")
    elif dry_run:
        print("🔍 Dry run - no changes made")
        for p in proposals:
            result = apply_improvement(p, dry_run=True)
            print(f"   {result}")


if __name__ == '__main__':
    main()
