#!/usr/bin/env python3
"""
Per-turn cost tracker for Opus.

Two modes:
1. Estimate: Theoretical cost based on context size (less accurate)
2. Real: Actual cost from session data (accurate)

Pricing (Opus):
- Input: $15/1M tokens
- Cache read: $1.50/1M tokens (0.1×)
- Cache write: $18.75/1M tokens (1.25×)
- Output: $75/1M tokens

Usage:
    python3 scripts/turn-cost.py real           # Last N turns from session
    python3 scripts/turn-cost.py real --last 10 # Last 10 turns
    python3 scripts/turn-cost.py stats          # Session cost distribution
    python3 scripts/turn-cost.py estimate -o 500  # Estimate for 500 char output
"""

import argparse
import json
from pathlib import Path
from datetime import datetime

# Opus pricing per 1M tokens (corrected)
PRICE_INPUT = 15.00
PRICE_CACHE_READ = 1.50  # 0.1× input (was incorrectly 1.875)
PRICE_CACHE_WRITE = 18.75  # 1.25× input
PRICE_OUTPUT = 75.00

MAX_CONTEXT = 200000
CHARS_PER_TOKEN = 4

SESSIONS_DIR = Path.home() / ".openclaw" / "agents" / "main" / "sessions"

def get_latest_session() -> Path:
    """Get the most recent session file."""
    sessions = sorted(SESSIONS_DIR.glob("*.jsonl"), 
                      key=lambda x: x.stat().st_mtime, reverse=True)
    return sessions[0] if sessions else None

def get_real_costs(last_n: int = 5) -> list:
    """Get actual costs from current session."""
    session = get_latest_session()
    if not session:
        return []
    
    costs = []
    with open(session) as f:
        for line in f:
            try:
                d = json.loads(line)
                if 'message' in d and 'usage' in d['message']:
                    u = d['message']['usage']
                    c = u.get('cost', {})
                    if c.get('total'):
                        costs.append({
                            'cost': c['total'],
                            'input': u.get('input', 0),
                            'output': u.get('output', 0),
                            'cache_read': u.get('cacheRead', 0),
                            'cache_write': u.get('cacheWrite', 0),
                        })
            except:
                pass
    
    return costs[-last_n:] if costs else []

def get_session_stats() -> dict:
    """Get cost statistics for current session."""
    session = get_latest_session()
    if not session:
        return {}
    
    costs = []
    with open(session) as f:
        for line in f:
            try:
                d = json.loads(line)
                if 'message' in d and 'usage' in d['message']:
                    c = d['message']['usage'].get('cost', {}).get('total', 0)
                    if c > 0:
                        costs.append(c)
            except:
                pass
    
    if not costs:
        return {}
    
    return {
        'turns': len(costs),
        'total': sum(costs),
        'avg': sum(costs) / len(costs),
        'min': min(costs),
        'max': max(costs),
        'distribution': {
            '<$0.10': sum(1 for c in costs if c < 0.10),
            '$0.10-0.20': sum(1 for c in costs if 0.10 <= c < 0.20),
            '$0.20-0.50': sum(1 for c in costs if 0.20 <= c < 0.50),
            '$0.50-1.00': sum(1 for c in costs if 0.50 <= c < 1.00),
            '>$1.00': sum(1 for c in costs if c >= 1.00),
        }
    }

def estimate_cost(output_chars: int, input_chars: int = 100, 
                  context_pct: float = 50, cache_rate: float = 0.95) -> dict:
    """Estimate cost (less accurate than real)."""
    context_tokens = int((context_pct / 100) * MAX_CONTEXT)
    cached = int(context_tokens * cache_rate)
    uncached = context_tokens - cached
    
    output_tokens = output_chars // CHARS_PER_TOKEN
    input_tokens = input_chars // CHARS_PER_TOKEN
    
    cost = (
        (cached / 1e6) * PRICE_CACHE_READ +
        (uncached / 1e6) * PRICE_CACHE_WRITE +
        (input_tokens / 1e6) * PRICE_INPUT +
        (output_tokens / 1e6) * PRICE_OUTPUT
    )
    
    return {
        'estimated_cost': round(cost, 4),
        'context_pct': context_pct,
        'output_tokens': output_tokens,
        'note': 'Estimate only - use "real" for actual costs'
    }

def main():
    parser = argparse.ArgumentParser(description="Turn cost tracker")
    parser.add_argument("mode", choices=["real", "stats", "estimate"], 
                        default="stats", nargs="?")
    parser.add_argument("--last", "-n", type=int, default=5,
                        help="Number of recent turns (real mode)")
    parser.add_argument("--output-chars", "-o", type=int, default=500)
    parser.add_argument("--context-pct", "-c", type=float, default=50)
    
    args = parser.parse_args()
    
    if args.mode == "real":
        costs = get_real_costs(args.last)
        if not costs:
            print("No cost data found")
            return
        print(f"Last {len(costs)} turns (actual cost):")
        for i, c in enumerate(costs, 1):
            print(f"  {i}. ${c['cost']:.4f} (out:{c['output']:,} cache:{c['cache_read']:,})")
        total = sum(c['cost'] for c in costs)
        print(f"  Total: ${total:.4f} | Avg: ${total/len(costs):.4f}")
        
    elif args.mode == "stats":
        stats = get_session_stats()
        if not stats:
            print("No session data")
            return
        print(f"Session Cost Stats:")
        print(f"  Turns: {stats['turns']:,}")
        print(f"  Total: ${stats['total']:.2f}")
        print(f"  Avg:   ${stats['avg']:.4f}")
        print(f"  Range: ${stats['min']:.4f} - ${stats['max']:.4f}")
        print(f"  Distribution:")
        for bucket, count in stats['distribution'].items():
            pct = count / stats['turns'] * 100
            bar = '█' * int(pct / 5)
            print(f"    {bucket:12} {count:4} ({pct:5.1f}%) {bar}")
            
    elif args.mode == "estimate":
        est = estimate_cost(args.output_chars, context_pct=args.context_pct)
        print(f"Estimated: ${est['estimated_cost']:.4f}")
        print(f"  ({est['note']})")

if __name__ == "__main__":
    main()
