#!/usr/bin/env python3
"""
Per-turn cost estimator for Opus.

Estimates cost based on:
- Context size (from session rotation script or estimate)
- Input tokens (prompt + context)
- Output tokens (response length)

Pricing (Opus):
- Input: $15/1M tokens
- Input (cache read): $1.875/1M tokens  
- Input (cache write): $18.75/1M tokens
- Output: $75/1M tokens

Usage:
    python3 scripts/turn-cost.py --output-chars 500
    python3 scripts/turn-cost.py --output-chars 2000 --context-pct 70
"""

import argparse
import json
from pathlib import Path
from datetime import datetime

# Opus pricing per 1M tokens
PRICE_INPUT = 15.00
PRICE_CACHE_READ = 1.875
PRICE_CACHE_WRITE = 18.75
PRICE_OUTPUT = 75.00

# Model context
MAX_CONTEXT = 200000  # tokens

# Estimates
CHARS_PER_TOKEN = 4  # rough estimate
SYSTEM_PROMPT_TOKENS = 50000  # baseline system prompt + workspace files

def estimate_turn_cost(
    output_chars: int,
    context_pct: float = None,
    input_chars: int = 500,  # user message
    cache_hit_rate: float = 0.90  # most of system prompt is cached
) -> dict:
    """Estimate cost for a single turn."""
    
    # Get context percentage if not provided
    if context_pct is None:
        # Try to read from session-rotation output or estimate
        context_pct = 70  # default estimate
    
    # Calculate tokens
    total_context_tokens = int((context_pct / 100) * MAX_CONTEXT)
    
    # New input this turn (user message)
    new_input_tokens = input_chars // CHARS_PER_TOKEN
    
    # Output tokens
    output_tokens = output_chars // CHARS_PER_TOKEN
    
    # Context breakdown
    cached_tokens = int(total_context_tokens * cache_hit_rate)
    uncached_tokens = total_context_tokens - cached_tokens
    
    # Cost calculation
    cache_read_cost = (cached_tokens / 1_000_000) * PRICE_CACHE_READ
    cache_write_cost = (uncached_tokens / 1_000_000) * PRICE_CACHE_WRITE
    new_input_cost = (new_input_tokens / 1_000_000) * PRICE_INPUT
    output_cost = (output_tokens / 1_000_000) * PRICE_OUTPUT
    
    total_cost = cache_read_cost + cache_write_cost + new_input_cost + output_cost
    
    return {
        "context_pct": context_pct,
        "context_tokens": total_context_tokens,
        "cached_tokens": cached_tokens,
        "uncached_tokens": uncached_tokens,
        "new_input_tokens": new_input_tokens,
        "output_tokens": output_tokens,
        "cache_read_cost": round(cache_read_cost, 4),
        "cache_write_cost": round(cache_write_cost, 4),
        "new_input_cost": round(new_input_cost, 4),
        "output_cost": round(output_cost, 4),
        "total_cost": round(total_cost, 4)
    }

def format_cost(cost_data: dict) -> str:
    """Format cost for display."""
    return f"~${cost_data['total_cost']:.2f}"

def format_detailed(cost_data: dict) -> str:
    """Detailed breakdown."""
    return f"""Turn Cost Estimate:
  Context: {cost_data['context_pct']}% ({cost_data['context_tokens']:,} tokens)
    - Cached: {cost_data['cached_tokens']:,} → ${cost_data['cache_read_cost']:.4f}
    - Uncached: {cost_data['uncached_tokens']:,} → ${cost_data['cache_write_cost']:.4f}
  New input: {cost_data['new_input_tokens']:,} tokens → ${cost_data['new_input_cost']:.4f}
  Output: {cost_data['output_tokens']:,} tokens → ${cost_data['output_cost']:.4f}
  ─────────────────────
  TOTAL: ${cost_data['total_cost']:.2f}"""

def log_turn(cost_data: dict, note: str = None):
    """Log turn cost to daily file."""
    log_file = Path(__file__).parent.parent / "memory" / "turn-costs.jsonl"
    entry = {
        "ts": datetime.utcnow().isoformat(),
        **cost_data
    }
    if note:
        entry["note"] = note
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Estimate per-turn Opus cost")
    parser.add_argument("--output-chars", "-o", type=int, default=1000,
                        help="Output character count")
    parser.add_argument("--input-chars", "-i", type=int, default=500,
                        help="Input (user message) character count")
    parser.add_argument("--context-pct", "-c", type=float, default=None,
                        help="Context percentage (0-100)")
    parser.add_argument("--cache-rate", type=float, default=0.90,
                        help="Cache hit rate (0-1)")
    parser.add_argument("--detailed", "-d", action="store_true",
                        help="Show detailed breakdown")
    parser.add_argument("--log", action="store_true",
                        help="Log to turn-costs.jsonl")
    parser.add_argument("--note", type=str, default=None,
                        help="Note for log entry")
    
    args = parser.parse_args()
    
    cost = estimate_turn_cost(
        output_chars=args.output_chars,
        context_pct=args.context_pct,
        input_chars=args.input_chars,
        cache_hit_rate=args.cache_rate
    )
    
    if args.detailed:
        print(format_detailed(cost))
    else:
        print(format_cost(cost))
    
    if args.log:
        log_turn(cost, args.note)
