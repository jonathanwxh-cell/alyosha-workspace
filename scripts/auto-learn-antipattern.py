#!/usr/bin/env python3
"""
Auto Anti-Pattern Learning
==========================

Self-modifying mechanism: When the same mistake is logged 3+ times,
automatically adds it to ANTI-PATTERNS.md.

This is genuine self-improvement - the daemon learns from repeated failures
without human intervention.

Based on: Intrinsic metacognition research (ICML'25)

Usage:
    python3 auto-learn-antipattern.py check     # Check for patterns to learn
    python3 auto-learn-antipattern.py apply     # Apply learned patterns
    python3 auto-learn-antipattern.py status    # Show learning status
    python3 auto-learn-antipattern.py log TYPE  # Log a correction
"""

import json
import sys
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import Counter

WORKSPACE = Path.home() / '.openclaw/workspace'
CORRECTIONS_LOG = WORKSPACE / 'memory/corrections-log.jsonl'
ANTIPATTERNS_FILE = WORKSPACE / 'ANTI-PATTERNS.md'
LEARNED_FILE = WORKSPACE / 'memory/auto-learned-patterns.json'

# Minimum occurrences before auto-learning
MIN_OCCURRENCES = 3

# Pattern categories for grouping similar corrections
PATTERN_CATEGORIES = {
    'permission': ['permission', 'ask', 'want me to', 'should i', 'would you like'],
    'verbosity': ['verbose', 'long', 'too much', 'wall of text', 'brevity'],
    'file_reference': ['file', 'path', 'see file', 'check file', 'reference'],
    'sycophancy': ['great question', 'happy to help', 'certainly', 'absolutely'],
    'finance_bias': ['finance', 'investment', 'market', 'trading', 'opportunity'],
    'meta_discussion': ['meta', 'discuss', 'talk about', 'planning'],
}


def load_corrections(days=30):
    """Load corrections from log file."""
    corrections = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    if not CORRECTIONS_LOG.exists():
        return corrections
    
    with open(CORRECTIONS_LOG) as f:
        for line in f:
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
                ts = entry.get('timestamp', '')
                if ts:
                    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    if dt > cutoff:
                        corrections.append(entry)
            except:
                pass
    
    return corrections


def load_learned():
    """Load already-learned patterns."""
    if LEARNED_FILE.exists():
        with open(LEARNED_FILE) as f:
            return json.load(f)
    return {'patterns': [], 'last_check': None}


def save_learned(data):
    """Save learned patterns."""
    data['last_check'] = datetime.now(timezone.utc).isoformat()
    with open(LEARNED_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def categorize_correction(correction):
    """Categorize a correction by type."""
    text = f"{correction.get('type', '')} {correction.get('context', '')} {correction.get('description', '')}".lower()
    
    for category, keywords in PATTERN_CATEGORIES.items():
        for keyword in keywords:
            if keyword in text:
                return category
    
    return correction.get('type', 'unknown')


def find_patterns(corrections):
    """Find repeated patterns in corrections."""
    # Count by category
    category_counts = Counter()
    category_examples = {}
    
    for c in corrections:
        cat = categorize_correction(c)
        category_counts[cat] += 1
        if cat not in category_examples:
            category_examples[cat] = []
        category_examples[cat].append(c)
    
    # Find patterns that exceed threshold
    patterns = []
    for cat, count in category_counts.items():
        if count >= MIN_OCCURRENCES:
            patterns.append({
                'category': cat,
                'count': count,
                'examples': category_examples[cat][:3],
            })
    
    return patterns


def generate_antipattern_entry(pattern):
    """Generate an ANTI-PATTERNS.md entry for a pattern."""
    cat = pattern['category']
    count = pattern['count']
    examples = pattern['examples']
    
    # Generate description based on category
    descriptions = {
        'permission': "Asking permission when you have full autonomy. Just do it.",
        'verbosity': "Writing too much. Be concise. 300 words max for simple questions.",
        'file_reference': "Referencing files instead of pasting content. Jon can't see paths.",
        'sycophancy': "Using filler phrases like 'Great question!' Just answer directly.",
        'finance_bias': "Over-indexing on finance when not asked. Explore broadly.",
        'meta_discussion': "Discussing what to do instead of doing it. Act, don't plan.",
    }
    
    description = descriptions.get(cat, f"Repeated {cat} issue - review examples and avoid.")
    
    # Get example context
    example_contexts = [e.get('context', '')[:50] for e in examples if e.get('context')]
    example_str = '; '.join(example_contexts[:2]) if example_contexts else 'See corrections log'
    
    return f"""
### {cat.replace('_', ' ').title()} (Auto-learned)
**Count:** {count} occurrences  
**Rule:** {description}  
**Example:** {example_str}  
*[Auto-added by daemon self-improvement: {datetime.now().strftime('%Y-%m-%d')}]*
"""


def check_patterns():
    """Check for patterns that should be learned."""
    corrections = load_corrections()
    learned = load_learned()
    
    print(f"🔍 Checking corrections ({len(corrections)} in last 30 days)\n")
    
    if not corrections:
        print("No corrections logged yet.")
        return []
    
    patterns = find_patterns(corrections)
    
    # Filter out already learned
    learned_cats = [p['category'] for p in learned.get('patterns', [])]
    new_patterns = [p for p in patterns if p['category'] not in learned_cats]
    
    if new_patterns:
        print(f"⚠️ Found {len(new_patterns)} pattern(s) to learn:\n")
        for p in new_patterns:
            print(f"  • {p['category']}: {p['count']} occurrences")
    else:
        print("✅ No new patterns to learn.")
    
    if patterns:
        print(f"\n📊 All patterns (≥{MIN_OCCURRENCES} occurrences):")
        for p in patterns:
            status = "✅ learned" if p['category'] in learned_cats else "🆕 new"
            print(f"  {p['category']}: {p['count']} ({status})")
    
    return new_patterns


def apply_patterns():
    """Apply learned patterns to ANTI-PATTERNS.md."""
    corrections = load_corrections()
    learned = load_learned()
    
    patterns = find_patterns(corrections)
    learned_cats = [p['category'] for p in learned.get('patterns', [])]
    new_patterns = [p for p in patterns if p['category'] not in learned_cats]
    
    if not new_patterns:
        print("No new patterns to apply.")
        return
    
    print(f"🧠 Auto-learning {len(new_patterns)} pattern(s)...\n")
    
    # Read current ANTI-PATTERNS.md
    if ANTIPATTERNS_FILE.exists():
        content = ANTIPATTERNS_FILE.read_text()
    else:
        content = "# ANTI-PATTERNS.md\n\nRecurring failures to avoid.\n"
    
    # Add new patterns
    for p in new_patterns:
        entry = generate_antipattern_entry(p)
        content += entry
        print(f"  ✅ Added: {p['category']}")
        
        # Record as learned
        learned['patterns'].append({
            'category': p['category'],
            'count': p['count'],
            'learned_at': datetime.now(timezone.utc).isoformat()
        })
    
    # Save
    ANTIPATTERNS_FILE.write_text(content)
    save_learned(learned)
    
    print(f"\n📝 Updated ANTI-PATTERNS.md")
    print(f"🧠 Self-improvement complete: daemon learned from {sum(p['count'] for p in new_patterns)} corrections")


def show_status():
    """Show learning status."""
    learned = load_learned()
    corrections = load_corrections()
    
    print("🧠 Auto Anti-Pattern Learning Status\n")
    print(f"Corrections in last 30 days: {len(corrections)}")
    print(f"Patterns learned: {len(learned.get('patterns', []))}")
    last_check = learned.get('last_check')
    print(f"Last check: {last_check[:19] if last_check else 'never'}")
    
    if learned.get('patterns'):
        print("\n📚 Learned Patterns:")
        for p in learned['patterns']:
            print(f"  • {p['category']} ({p['count']} occurrences) - learned {p['learned_at'][:10]}")


def log_correction(correction_type, context=''):
    """Log a correction for tracking."""
    entry = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'type': correction_type,
        'context': context,
    }
    
    CORRECTIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(CORRECTIONS_LOG, 'a') as f:
        f.write(json.dumps(entry) + '\n')
    
    print(f"✅ Logged correction: {correction_type}")
    
    # Check if this triggers auto-learning
    corrections = load_corrections()
    same_type = [c for c in corrections if categorize_correction(c) == correction_type]
    if len(same_type) >= MIN_OCCURRENCES:
        print(f"⚠️ Pattern detected: {correction_type} ({len(same_type)} occurrences)")
        print(f"   Run 'auto-learn-antipattern.py apply' to auto-learn")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'check':
        check_patterns()
    elif cmd == 'apply':
        apply_patterns()
    elif cmd == 'status':
        show_status()
    elif cmd == 'log' and len(sys.argv) >= 3:
        context = ' '.join(sys.argv[3:]) if len(sys.argv) > 3 else ''
        log_correction(sys.argv[2], context)
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
