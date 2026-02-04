#!/usr/bin/env python3
"""
Auto Anti-Pattern Detector
==========================

Self-modifying agent mechanism: Automatically detects failure patterns
and adds them to ANTI-PATTERNS.md to prevent future occurrences.

This is a concrete implementation of the SICA (Self-Improving Coding Agent)
pattern - the daemon modifying its own instruction files based on outcomes.

Usage:
    python3 auto-antipattern.py detect "description of failure"
    python3 auto-antipattern.py add "pattern" "wrong_example" "right_example"
    python3 auto-antipattern.py check "proposed action"
    python3 auto-antipattern.py stats
    python3 auto-antipattern.py recent

Research basis:
- SICA: Self-Improving Coding Agent (17% → 53% on SWE-Bench)
- Gödel Agent: Runtime self-modification
- Reflexion: Verbal reinforcement learning
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path

ANTIPATTERN_FILE = Path.home() / '.openclaw/workspace/ANTI-PATTERNS.md'
REFLECTIONS_FILE = Path.home() / '.openclaw/workspace/memory/reflections.jsonl'
PATTERN_LOG = Path.home() / '.openclaw/workspace/memory/antipattern-log.jsonl'

def load_antipatterns():
    """Load current anti-patterns from markdown file."""
    if not ANTIPATTERN_FILE.exists():
        return []
    
    content = ANTIPATTERN_FILE.read_text()
    # Extract pattern names (## 🚫 NEVER...)
    patterns = re.findall(r'## 🚫 (.+)', content)
    return patterns

def load_reflections(n=20):
    """Load recent reflections looking for failures."""
    if not REFLECTIONS_FILE.exists():
        return []
    
    reflections = []
    with open(REFLECTIONS_FILE) as f:
        for line in f:
            if line.strip():
                try:
                    reflections.append(json.loads(line))
                except:
                    pass
    
    # Filter for failures/partial outcomes
    failures = [r for r in reflections if r.get('outcome') in ('failure', 'partial')]
    return failures[-n:]

def detect_pattern(description: str):
    """Analyze a failure and suggest an anti-pattern."""
    # Common failure patterns to detect
    detectors = [
        {
            'keywords': ['permission', 'ask', 'should i', 'want me to'],
            'pattern': 'ASKING PERMISSION',
            'wrong': 'Want me to...? / Should I...?',
            'right': 'Just do it. Report in past tense.'
        },
        {
            'keywords': ['file path', 'see file', 'check file', 'saved to'],
            'pattern': 'REFERENCING FILE PATHS',
            'wrong': 'See memory/file.md for details',
            'right': 'Paste the actual content in the message'
        },
        {
            'keywords': ['attached', 'attachment'],
            'pattern': 'SAYING SEE ATTACHED',
            'wrong': 'See attached file',
            'right': 'Show content directly'
        },
        {
            'keywords': ['api key', 'token', 'secret', 'credential'],
            'pattern': 'NOT CHECKING EXISTING KEYS',
            'wrong': 'Asking Jon for API key',
            'right': 'Check ~/.secure/ first'
        },
        {
            'keywords': ['repeat', 'again', 'already said', 'mentioned before'],
            'pattern': 'REPEATING INFORMATION',
            'wrong': 'Surfacing already-covered topics',
            'right': 'Check surface-tracker.py first'
        },
        {
            'keywords': ['wall of text', 'too long', 'verbose'],
            'pattern': 'WALLS OF TEXT',
            'wrong': 'Long unstructured messages',
            'right': 'Lead with insight, use bullets, be concise'
        },
        {
            'keywords': ['config', 'not implemented', 'dead code'],
            'pattern': 'CONFIG WITHOUT IMPLEMENTATION',
            'wrong': 'Config exists but code doesnt use it',
            'right': 'Audit config vs implementation'
        }
    ]
    
    desc_lower = description.lower()
    
    for detector in detectors:
        if any(kw in desc_lower for kw in detector['keywords']):
            return {
                'detected': True,
                'pattern': detector['pattern'],
                'wrong': detector['wrong'],
                'right': detector['right'],
                'confidence': 'high'
            }
    
    # No known pattern matched
    return {
        'detected': False,
        'suggestion': 'Manual review needed - no known pattern matched',
        'description': description
    }

def add_antipattern(pattern: str, wrong: str, right: str):
    """Add a new anti-pattern to ANTI-PATTERNS.md"""
    if not ANTIPATTERN_FILE.exists():
        print("❌ ANTI-PATTERNS.md not found")
        return False
    
    content = ANTIPATTERN_FILE.read_text()
    
    # Check if pattern already exists
    if pattern.upper() in content.upper():
        print(f"⚠️ Pattern '{pattern}' already exists")
        return False
    
    # Find insertion point (before Pre-Flight Checklist)
    insertion_point = content.find('## Pre-Flight Checklist')
    if insertion_point == -1:
        insertion_point = len(content)
    
    # Create new section
    new_section = f"""
---

## 🚫 {pattern.upper()}

**WRONG:**
- {wrong}

**RIGHT:**
- {right}

*Auto-detected: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
    
    # Insert
    new_content = content[:insertion_point] + new_section + '\n' + content[insertion_point:]
    ANTIPATTERN_FILE.write_text(new_content)
    
    # Log
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': 'add',
        'pattern': pattern,
        'wrong': wrong,
        'right': right
    }
    with open(PATTERN_LOG, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
    
    print(f"✅ Added anti-pattern: {pattern}")
    return True

def check_action(proposed: str):
    """Check if a proposed action matches any anti-patterns."""
    patterns = load_antipatterns()
    content = ANTIPATTERN_FILE.read_text() if ANTIPATTERN_FILE.exists() else ""
    
    proposed_lower = proposed.lower()
    matches = []
    
    # Check for permission-asking
    permission_phrases = ['want me to', 'should i', 'would you like', 'let me know if']
    if any(p in proposed_lower for p in permission_phrases):
        matches.append('ASKING PERMISSION')
    
    # Check for file paths
    if re.search(r'(see |check |saved to |at )?(memory/|scripts/|tools/|docs/)', proposed_lower):
        if 'paste' not in proposed_lower and 'content' not in proposed_lower:
            matches.append('REFERENCING FILE PATHS')
    
    # Check for attached
    if 'attached' in proposed_lower or 'attachment' in proposed_lower:
        matches.append('SAYING SEE ATTACHED')
    
    if matches:
        print(f"⚠️ ANTI-PATTERN DETECTED in proposed action:")
        for m in matches:
            print(f"   🚫 {m}")
        return False
    
    print("✅ No anti-patterns detected")
    return True

def stats():
    """Show anti-pattern statistics."""
    patterns = load_antipatterns()
    failures = load_reflections(50)
    
    print("📊 Anti-Pattern Statistics")
    print("=" * 40)
    print(f"Patterns defined: {len(patterns)}")
    print(f"Recent failures analyzed: {len(failures)}")
    print()
    print("Patterns:")
    for p in patterns:
        print(f"  🚫 {p}")
    
    if PATTERN_LOG.exists():
        with open(PATTERN_LOG) as f:
            logs = [json.loads(l) for l in f if l.strip()]
        print(f"\nAuto-added patterns: {len(logs)}")

def recent():
    """Show recent failures that could become anti-patterns."""
    failures = load_reflections(10)
    
    if not failures:
        print("No recent failures found")
        return
    
    print("🔍 Recent Failures (potential anti-patterns)")
    print("=" * 50)
    
    for f in failures:
        task = f.get('task', 'unknown')
        lesson = f.get('lesson', 'no lesson')
        print(f"\n📍 {task}")
        print(f"   Lesson: {lesson}")
        
        # Try to detect pattern
        detection = detect_pattern(lesson)
        if detection.get('detected'):
            print(f"   → Suggested pattern: {detection['pattern']}")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1]
    
    if cmd == 'detect' and len(sys.argv) >= 3:
        description = ' '.join(sys.argv[2:])
        result = detect_pattern(description)
        print(json.dumps(result, indent=2))
        
        if result.get('detected'):
            print(f"\n💡 Suggested anti-pattern: {result['pattern']}")
            print(f"   Wrong: {result['wrong']}")
            print(f"   Right: {result['right']}")
            print(f"\n   To add: python3 auto-antipattern.py add \"{result['pattern']}\" \"{result['wrong']}\" \"{result['right']}\"")
    
    elif cmd == 'add' and len(sys.argv) >= 5:
        pattern = sys.argv[2]
        wrong = sys.argv[3]
        right = sys.argv[4]
        add_antipattern(pattern, wrong, right)
    
    elif cmd == 'check' and len(sys.argv) >= 3:
        proposed = ' '.join(sys.argv[2:])
        check_action(proposed)
    
    elif cmd == 'stats':
        stats()
    
    elif cmd == 'recent':
        recent()
    
    else:
        print(__doc__)

if __name__ == '__main__':
    main()
