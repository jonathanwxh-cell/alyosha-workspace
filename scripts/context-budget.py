#!/usr/bin/env python3
"""
Context Budget Tracker
======================

Monitors token counts in key context files to prevent bloat.

Usage:
    python3 context-budget.py              # Show current usage
    python3 context-budget.py --alert      # Alert if over budget
    python3 context-budget.py --history    # Show trend over time

Context rot happens as token count increases.
Keep files lean for better model performance.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / '.openclaw/workspace'

# Token budget targets (approximate, 1 token ≈ 4 chars)
BUDGETS = {
    'HEARTBEAT.md': 3000,      # Keep lean for every heartbeat
    'MEMORY.md': 4000,         # Long-term memory
    'AGENTS.md': 2000,         # Core instructions
    'SOUL.md': 500,            # Identity
    'USER.md': 1000,           # User profile
    'TOOLS.md': 1500,          # Tool notes
}

def estimate_tokens(text: str) -> int:
    """Rough token estimate (1 token ≈ 4 chars for English)"""
    return len(text) // 4

def get_file_stats(filepath: Path) -> dict:
    """Get stats for a file"""
    if not filepath.exists():
        return {'exists': False}
    
    content = filepath.read_text()
    chars = len(content)
    lines = content.count('\n') + 1
    tokens = estimate_tokens(content)
    
    return {
        'exists': True,
        'chars': chars,
        'lines': lines,
        'tokens': tokens
    }

def check_budgets():
    """Check all context files against budgets"""
    results = []
    total_tokens = 0
    
    for filename, budget in BUDGETS.items():
        filepath = WORKSPACE / filename
        stats = get_file_stats(filepath)
        
        if not stats['exists']:
            continue
        
        tokens = stats['tokens']
        total_tokens += tokens
        pct = (tokens / budget) * 100
        status = '🟢' if pct < 80 else '🟡' if pct < 100 else '🔴'
        
        results.append({
            'file': filename,
            'tokens': tokens,
            'budget': budget,
            'pct': pct,
            'status': status
        })
    
    return results, total_tokens

def print_report():
    """Print context budget report"""
    results, total = check_budgets()
    
    print("\n📊 Context Budget Report")
    print("=" * 50)
    print(f"{'File':<20} {'Tokens':>8} {'Budget':>8} {'Usage':>10}")
    print("-" * 50)
    
    over_budget = []
    for r in sorted(results, key=lambda x: -x['pct']):
        usage = f"{r['pct']:.0f}%"
        print(f"{r['status']} {r['file']:<18} {r['tokens']:>8} {r['budget']:>8} {usage:>10}")
        if r['pct'] > 100:
            over_budget.append(r['file'])
    
    print("-" * 50)
    print(f"   {'TOTAL':<18} {total:>8}")
    print()
    
    if over_budget:
        print("⚠️  Over budget:", ', '.join(over_budget))
        print("   Consider compressing or moving content to references/")
    
    # Memory files
    memory_dir = WORKSPACE / 'memory'
    if memory_dir.exists():
        memory_tokens = 0
        memory_files = list(memory_dir.glob('*.json')) + list(memory_dir.glob('*.md'))
        for f in memory_files:
            if f.is_file():
                memory_tokens += estimate_tokens(f.read_text())
        print(f"\n📁 memory/ folder: ~{memory_tokens:,} tokens across {len(memory_files)} files")
    
    return over_budget

def log_snapshot():
    """Log current state for trend tracking"""
    results, total = check_budgets()
    
    log_file = WORKSPACE / 'data' / 'context-budget-log.jsonl'
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    entry = {
        'timestamp': datetime.now().isoformat(),
        'total_tokens': total,
        'files': {r['file']: r['tokens'] for r in results}
    }
    
    with open(log_file, 'a') as f:
        f.write(json.dumps(entry) + '\n')
    
    print(f"📝 Logged to {log_file}")

def main():
    if '--alert' in sys.argv:
        over_budget = print_report()
        sys.exit(1 if over_budget else 0)
    elif '--history' in sys.argv:
        log_file = WORKSPACE / 'data' / 'context-budget-log.jsonl'
        if log_file.exists():
            lines = log_file.read_text().strip().split('\n')[-10:]
            print("\n📈 Recent context budget history:")
            for line in lines:
                entry = json.loads(line)
                print(f"  {entry['timestamp'][:10]}: {entry['total_tokens']:,} tokens")
        else:
            print("No history yet. Run without --history first.")
    elif '--log' in sys.argv:
        print_report()
        log_snapshot()
    else:
        print_report()

if __name__ == '__main__':
    main()
