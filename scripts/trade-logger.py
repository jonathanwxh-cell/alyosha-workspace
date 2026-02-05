#!/usr/bin/env python3
"""
Trade Logger - Capture every trading decision for learning loop

Usage:
    # Log a PASS decision
    python3 trade-logger.py pass RTX 6.8 '{"business_quality":8,"management":6,"financials":7,"valuation":6,"technicals":7,"sentiment":7,"catalyst":6}'
    
    # Log an EXECUTE decision
    python3 trade-logger.py execute RTX 7.8 '{"business_quality":8,...}' --strategy "Bull Put Spread" --entry 196.74
    
    # Update outcome after trade closes
    python3 trade-logger.py outcome RTX 2026-02-05 --pnl 15.5 --exit-reason "target"
    
    # View recent decisions
    python3 trade-logger.py list 10
    
    # Calibration stats
    python3 trade-logger.py stats
"""

import json
import sys
from pathlib import Path
from datetime import datetime

TRADE_LOG = Path.home() / '.openclaw/workspace/memory/goals/trading/trade-log.jsonl'


def log_decision(action: str, ticker: str, score: float, dimensions: dict, **kwargs):
    """Log a trading decision."""
    TRADE_LOG.parent.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "ticker": ticker.upper(),
        "action": action.upper(),
        "final_score": score,
        "dimensions": dimensions,
        "outcome": None,
        "pnl_percent": None,
        "alpha": None,
        **kwargs
    }
    
    with open(TRADE_LOG, 'a') as f:
        f.write(json.dumps(entry) + '\n')
    
    print(f"✓ Logged {action.upper()} on {ticker} (score: {score})")
    return entry


def update_outcome(ticker: str, date: str, pnl: float, exit_reason: str = None, market_return: float = None):
    """Update a logged trade with its outcome."""
    if not TRADE_LOG.exists():
        print("No trade log found")
        return
    
    lines = TRADE_LOG.read_text().strip().split('\n')
    updated = False
    new_lines = []
    
    for line in lines:
        entry = json.loads(line)
        if entry['ticker'] == ticker.upper() and entry['timestamp'].startswith(date):
            entry['outcome'] = 'WIN' if pnl > 0 else 'LOSS'
            entry['pnl_percent'] = pnl
            entry['exit_reason'] = exit_reason
            if market_return is not None:
                entry['market_return'] = market_return
                entry['alpha'] = pnl - market_return
            updated = True
            print(f"✓ Updated {ticker} ({date}): {pnl:+.1f}% → {entry['outcome']}")
        new_lines.append(json.dumps(entry))
    
    if updated:
        TRADE_LOG.write_text('\n'.join(new_lines) + '\n')
    else:
        print(f"No matching trade found for {ticker} on {date}")


def list_recent(n: int = 10):
    """List recent decisions."""
    if not TRADE_LOG.exists():
        print("No trade log found")
        return
    
    lines = TRADE_LOG.read_text().strip().split('\n')
    recent = lines[-n:] if len(lines) >= n else lines
    
    print(f"\n{'='*60}")
    print(f"RECENT TRADING DECISIONS (last {len(recent)})")
    print(f"{'='*60}\n")
    
    for line in recent:
        entry = json.loads(line)
        outcome = entry.get('outcome', 'PENDING')
        pnl = entry.get('pnl_percent')
        pnl_str = f"{pnl:+.1f}%" if pnl is not None else "—"
        
        print(f"{entry['timestamp'][:10]} | {entry['ticker']:5} | {entry['action']:7} | "
              f"Score: {entry['final_score']:.1f} | {outcome:7} | {pnl_str}")


def calc_stats():
    """Calculate calibration statistics."""
    if not TRADE_LOG.exists():
        print("No trade log found")
        return
    
    lines = TRADE_LOG.read_text().strip().split('\n')
    entries = [json.loads(line) for line in lines]
    
    executes = [e for e in entries if e['action'] == 'EXECUTE']
    with_outcome = [e for e in executes if e.get('outcome')]
    
    print(f"\n{'='*60}")
    print("FRAMEWORK CALIBRATION STATS")
    print(f"{'='*60}\n")
    
    print(f"Total decisions logged: {len(entries)}")
    print(f"  - EXECUTE: {len(executes)}")
    print(f"  - PASS: {len([e for e in entries if e['action'] == 'PASS'])}")
    print(f"  - With outcomes: {len(with_outcome)}")
    
    if len(with_outcome) < 5:
        print(f"\n⚠️  Need {5 - len(with_outcome)} more completed trades for calibration")
        return
    
    # Win rate by score bucket
    wins = [e for e in with_outcome if e['outcome'] == 'WIN']
    print(f"\nOverall win rate: {len(wins)/len(with_outcome)*100:.0f}%")
    
    # Score buckets
    buckets = {'7.5-8.0': [], '8.0-8.5': [], '8.5+': []}
    for e in with_outcome:
        score = e['final_score']
        if score >= 8.5:
            buckets['8.5+'].append(e)
        elif score >= 8.0:
            buckets['8.0-8.5'].append(e)
        else:
            buckets['7.5-8.0'].append(e)
    
    print("\nWin rate by score:")
    for bucket, trades in buckets.items():
        if trades:
            wins = len([t for t in trades if t['outcome'] == 'WIN'])
            print(f"  {bucket}: {wins}/{len(trades)} ({wins/len(trades)*100:.0f}%)")
    
    # Dimension correlation (simplified)
    if len(with_outcome) >= 10:
        print("\nDimension correlation with wins (need 20+ for reliability):")
        dims = ['business_quality', 'management', 'financials', 'valuation', 
                'technicals', 'sentiment', 'catalyst']
        
        for dim in dims:
            dim_scores = []
            outcomes = []
            for e in with_outcome:
                if e.get('dimensions') and dim in e['dimensions']:
                    dim_scores.append(e['dimensions'][dim])
                    outcomes.append(1 if e['outcome'] == 'WIN' else 0)
            
            if dim_scores:
                # Simple correlation: avg score for wins vs losses
                win_avg = sum(s for s, o in zip(dim_scores, outcomes) if o) / max(sum(outcomes), 1)
                loss_avg = sum(s for s, o in zip(dim_scores, outcomes) if not o) / max(len(outcomes) - sum(outcomes), 1)
                diff = win_avg - loss_avg
                signal = "📈" if diff > 0.5 else "📉" if diff < -0.5 else "➖"
                print(f"  {signal} {dim}: win_avg={win_avg:.1f}, loss_avg={loss_avg:.1f}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd in ('pass', 'execute') and len(sys.argv) >= 5:
        ticker = sys.argv[2]
        score = float(sys.argv[3])
        dimensions = json.loads(sys.argv[4])
        kwargs = {}
        
        # Parse optional args
        args = sys.argv[5:]
        i = 0
        while i < len(args):
            if args[i] == '--strategy' and i+1 < len(args):
                kwargs['strategy'] = args[i+1]
                i += 2
            elif args[i] == '--entry' and i+1 < len(args):
                kwargs['entry_price'] = float(args[i+1])
                i += 2
            else:
                i += 1
        
        log_decision(cmd, ticker, score, dimensions, **kwargs)
    
    elif cmd == 'outcome' and len(sys.argv) >= 4:
        ticker = sys.argv[2]
        date = sys.argv[3]
        pnl = None
        exit_reason = None
        market_return = None
        
        args = sys.argv[4:]
        i = 0
        while i < len(args):
            if args[i] == '--pnl' and i+1 < len(args):
                pnl = float(args[i+1])
                i += 2
            elif args[i] == '--exit-reason' and i+1 < len(args):
                exit_reason = args[i+1]
                i += 2
            elif args[i] == '--market' and i+1 < len(args):
                market_return = float(args[i+1])
                i += 2
            else:
                i += 1
        
        if pnl is not None:
            update_outcome(ticker, date, pnl, exit_reason, market_return)
        else:
            print("--pnl required")
    
    elif cmd == 'list':
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        list_recent(n)
    
    elif cmd == 'stats':
        calc_stats()
    
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
