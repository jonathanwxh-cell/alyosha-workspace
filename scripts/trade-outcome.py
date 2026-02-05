#!/usr/bin/env python3
"""
Trade Outcome Tracker

Logs trade outcomes for the feedback loop.
Connects results back to the research that led to the trade.

Usage:
    python3 scripts/trade-outcome.py log <ticker> <result> <return_pct> [options]
    python3 scripts/trade-outcome.py stats
    python3 scripts/trade-outcome.py analyze

Examples:
    python3 scripts/trade-outcome.py log RTX win 5.5 --strategy wheel_csp --sector industrials
    python3 scripts/trade-outcome.py log AAPL loss -3.2 --strategy pmcc --sector technology
    python3 scripts/trade-outcome.py stats
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

OUTCOMES_FILE = Path.home() / ".openclaw/workspace/memory/goals/trading/outcomes.jsonl"
WEIGHTS_FILE = Path.home() / ".openclaw/workspace/memory/goals/trading/learning-weights.json"
OUTCOMES_FILE.parent.mkdir(parents=True, exist_ok=True)


def log_outcome(ticker: str, result: str, return_pct: float, 
                strategy: str = None, sector: str = None,
                entry_score: float = None, entry_price: float = None,
                exit_price: float = None, days_held: int = None,
                thesis: str = None, what_worked: str = None, 
                what_failed: str = None):
    """Log a trade outcome."""
    
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ticker": ticker.upper(),
        "result": result.lower(),  # win/loss/breakeven
        "return_pct": float(return_pct),
        "strategy": strategy,
        "sector": sector,
        "entry_score": entry_score,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "days_held": days_held,
        "thesis": thesis,
        "what_worked": what_worked,
        "what_failed": what_failed
    }
    
    # Remove None values
    entry = {k: v for k, v in entry.items() if v is not None}
    
    with open(OUTCOMES_FILE, 'a') as f:
        f.write(json.dumps(entry) + '\n')
    
    return entry


def load_outcomes():
    """Load all outcomes."""
    outcomes = []
    if OUTCOMES_FILE.exists():
        with open(OUTCOMES_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        outcomes.append(json.loads(line))
                    except:
                        pass
    return outcomes


def get_stats():
    """Calculate outcome statistics."""
    outcomes = load_outcomes()
    
    if not outcomes:
        return {"total": 0, "message": "No outcomes yet"}
    
    wins = [o for o in outcomes if o.get('result') == 'win']
    losses = [o for o in outcomes if o.get('result') == 'loss']
    
    # By sector
    by_sector = {}
    for o in outcomes:
        sector = o.get('sector', 'unknown')
        if sector not in by_sector:
            by_sector[sector] = {'wins': 0, 'losses': 0, 'total_return': 0}
        if o.get('result') == 'win':
            by_sector[sector]['wins'] += 1
        elif o.get('result') == 'loss':
            by_sector[sector]['losses'] += 1
        by_sector[sector]['total_return'] += o.get('return_pct', 0)
    
    # By strategy
    by_strategy = {}
    for o in outcomes:
        strategy = o.get('strategy', 'unknown')
        if strategy not in by_strategy:
            by_strategy[strategy] = {'wins': 0, 'losses': 0, 'total_return': 0}
        if o.get('result') == 'win':
            by_strategy[strategy]['wins'] += 1
        elif o.get('result') == 'loss':
            by_strategy[strategy]['losses'] += 1
        by_strategy[strategy]['total_return'] += o.get('return_pct', 0)
    
    total_return = sum(o.get('return_pct', 0) for o in outcomes)
    
    return {
        "total_trades": len(outcomes),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": len(wins) / len(outcomes) if outcomes else 0,
        "total_return_pct": total_return,
        "avg_return_pct": total_return / len(outcomes) if outcomes else 0,
        "by_sector": by_sector,
        "by_strategy": by_strategy
    }


def analyze_for_adjustments():
    """Analyze outcomes and suggest weight adjustments."""
    outcomes = load_outcomes()
    
    if len(outcomes) < 5:
        return {
            "status": "insufficient_data",
            "message": f"Need at least 5 trades for analysis (have {len(outcomes)})",
            "adjustments": []
        }
    
    # Load current weights
    if WEIGHTS_FILE.exists():
        with open(WEIGHTS_FILE, 'r') as f:
            weights = json.load(f)
    else:
        return {"status": "error", "message": "No weights file found"}
    
    adjustments = []
    
    # Analyze sector performance
    by_sector = {}
    for o in outcomes:
        sector = o.get('sector', 'unknown')
        if sector not in by_sector:
            by_sector[sector] = {'wins': 0, 'total': 0}
        by_sector[sector]['total'] += 1
        if o.get('result') == 'win':
            by_sector[sector]['wins'] += 1
    
    for sector, perf in by_sector.items():
        if perf['total'] >= 3:  # Minimum sample
            win_rate = perf['wins'] / perf['total']
            current_weight = weights.get('sector_weights', {}).get(sector, 1.0)
            
            if win_rate > 0.65 and current_weight < 1.3:
                adjustments.append({
                    "type": "sector_weight",
                    "sector": sector,
                    "current": current_weight,
                    "suggested": min(current_weight * 1.1, 1.3),
                    "reason": f"Win rate {win_rate:.0%} > 65%"
                })
            elif win_rate < 0.35 and current_weight > 0.7:
                adjustments.append({
                    "type": "sector_weight",
                    "sector": sector,
                    "current": current_weight,
                    "suggested": max(current_weight * 0.9, 0.7),
                    "reason": f"Win rate {win_rate:.0%} < 35%"
                })
    
    # Analyze score threshold
    # If we're winning most trades, maybe threshold is too high (missing good ones)
    # If we're losing most, threshold too low
    win_rate = len([o for o in outcomes if o.get('result') == 'win']) / len(outcomes)
    current_threshold = weights.get('score_threshold', {}).get('current', 7.5)
    
    if win_rate > 0.7 and current_threshold > 7.0:
        adjustments.append({
            "type": "score_threshold",
            "current": current_threshold,
            "suggested": current_threshold - 0.25,
            "reason": f"Win rate {win_rate:.0%} high — may be too selective"
        })
    elif win_rate < 0.4 and current_threshold < 8.5:
        adjustments.append({
            "type": "score_threshold",
            "current": current_threshold,
            "suggested": current_threshold + 0.25,
            "reason": f"Win rate {win_rate:.0%} low — need higher bar"
        })
    
    return {
        "status": "ok",
        "total_trades": len(outcomes),
        "win_rate": win_rate,
        "adjustments": adjustments
    }


def apply_adjustment(adjustment_type: str, value: float, sector: str = None):
    """Apply a weight adjustment."""
    if not WEIGHTS_FILE.exists():
        return {"error": "No weights file"}
    
    with open(WEIGHTS_FILE, 'r') as f:
        weights = json.load(f)
    
    if adjustment_type == "score_threshold":
        old = weights['score_threshold']['current']
        weights['score_threshold']['current'] = value
        weights['score_threshold']['history'].append({
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "value": value,
            "reason": "feedback loop adjustment"
        })
    elif adjustment_type == "sector_weight" and sector:
        old = weights.get('sector_weights', {}).get(sector, 1.0)
        weights['sector_weights'][sector] = value
    else:
        return {"error": f"Unknown adjustment type: {adjustment_type}"}
    
    weights['meta']['lastUpdated'] = datetime.now(timezone.utc).isoformat()
    
    with open(WEIGHTS_FILE, 'w') as f:
        json.dump(weights, f, indent=2)
    
    return {"success": True, "type": adjustment_type, "old": old, "new": value}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'log':
        if len(sys.argv) < 5:
            print("Usage: trade-outcome.py log <ticker> <result> <return_pct> [--strategy X] [--sector Y]")
            return
        
        ticker = sys.argv[2]
        result = sys.argv[3]
        return_pct = float(sys.argv[4])
        
        # Parse optional args
        kwargs = {}
        i = 5
        while i < len(sys.argv):
            if sys.argv[i] == '--strategy' and i + 1 < len(sys.argv):
                kwargs['strategy'] = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--sector' and i + 1 < len(sys.argv):
                kwargs['sector'] = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--score' and i + 1 < len(sys.argv):
                kwargs['entry_score'] = float(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == '--days' and i + 1 < len(sys.argv):
                kwargs['days_held'] = int(sys.argv[i + 1])
                i += 2
            else:
                i += 1
        
        entry = log_outcome(ticker, result, return_pct, **kwargs)
        print(json.dumps(entry, indent=2))
    
    elif cmd == 'stats':
        stats = get_stats()
        print(json.dumps(stats, indent=2))
    
    elif cmd == 'analyze':
        analysis = analyze_for_adjustments()
        print(json.dumps(analysis, indent=2))
    
    elif cmd == 'apply':
        if len(sys.argv) < 4:
            print("Usage: trade-outcome.py apply <type> <value> [--sector X]")
            return
        adj_type = sys.argv[2]
        value = float(sys.argv[3])
        sector = None
        if '--sector' in sys.argv:
            idx = sys.argv.index('--sector')
            sector = sys.argv[idx + 1]
        result = apply_adjustment(adj_type, value, sector)
        print(json.dumps(result, indent=2))
    
    elif cmd == 'list':
        outcomes = load_outcomes()
        for o in outcomes[-10:]:
            ts = o.get('timestamp', '')[:10]
            ticker = o.get('ticker', '?')
            result = o.get('result', '?')
            ret = o.get('return_pct', 0)
            print(f"[{ts}] {ticker}: {result} {ret:+.1f}%")
    
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == '__main__':
    main()
