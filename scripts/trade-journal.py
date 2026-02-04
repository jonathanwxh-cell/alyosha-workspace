#!/usr/bin/env python3
"""
Trade Journal - Track trades, outcomes, and patterns

Helps Jon track speculative positions and learn from outcomes.
Based on insight: "tends to speculate more when bored"

Usage:
    python3 trade-journal.py add TICKER [--type TYPE] [--direction long/short] [--notes "..."]
    python3 trade-journal.py close TICKER [--outcome win/loss/breakeven] [--pnl X%] [--lesson "..."]
    python3 trade-journal.py open                    # List open positions
    python3 trade-journal.py history [--days N]     # Show recent trades
    python3 trade-journal.py stats                   # Win rate, patterns
    python3 trade-journal.py patterns               # Behavioral insights
"""

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import Counter

JOURNAL_FILE = Path.home() / '.openclaw/workspace/memory/trade-journal.jsonl'
PATTERNS_FILE = Path.home() / '.openclaw/workspace/memory/trading-patterns.json'


def load_trades():
    """Load all trades from journal."""
    trades = []
    if JOURNAL_FILE.exists():
        with open(JOURNAL_FILE) as f:
            for line in f:
                if line.strip():
                    try:
                        trades.append(json.loads(line))
                    except:
                        pass
    return trades


def save_trade(trade):
    """Append trade to journal."""
    JOURNAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(JOURNAL_FILE, 'a') as f:
        f.write(json.dumps(trade) + '\n')


def update_trade(ticker, updates):
    """Update an existing open trade."""
    trades = load_trades()
    updated = False
    
    # Find the most recent open trade for this ticker
    for i in range(len(trades) - 1, -1, -1):
        if trades[i].get('ticker', '').upper() == ticker.upper() and trades[i].get('status') == 'open':
            trades[i].update(updates)
            updated = True
            break
    
    if updated:
        # Rewrite file
        with open(JOURNAL_FILE, 'w') as f:
            for t in trades:
                f.write(json.dumps(t) + '\n')
    
    return updated


def add_trade(ticker, trade_type='stock', direction='long', notes=''):
    """Add a new trade to the journal."""
    now = datetime.now(timezone.utc)
    
    trade = {
        'ticker': ticker.upper(),
        'type': trade_type,  # stock, option, future
        'direction': direction,  # long, short
        'status': 'open',
        'opened': now.isoformat(),
        'opened_day': now.strftime('%A'),
        'opened_hour': (now.hour + 8) % 24,  # SGT
        'notes': notes,
    }
    
    save_trade(trade)
    print(f"📝 Logged: {direction.upper()} {ticker.upper()} ({trade_type})")
    if notes:
        print(f"   Notes: {notes}")
    
    # Check for warning patterns
    trades = load_trades()
    recent_opens = [t for t in trades 
                   if t.get('status') == 'open' 
                   and t.get('opened', '')[:10] == now.isoformat()[:10]]
    
    if len(recent_opens) > 2:
        print(f"\n⚠️  Warning: {len(recent_opens)} positions opened today. Feeling impulsive?")
    
    return trade


def close_trade(ticker, outcome='unknown', pnl=None, lesson=''):
    """Close a trade and record outcome."""
    now = datetime.now(timezone.utc)
    
    updates = {
        'status': 'closed',
        'closed': now.isoformat(),
        'outcome': outcome,  # win, loss, breakeven
        'lesson': lesson,
    }
    
    if pnl is not None:
        updates['pnl_pct'] = pnl
    
    if update_trade(ticker, updates):
        emoji = {'win': '✅', 'loss': '❌', 'breakeven': '➖'}.get(outcome, '❓')
        print(f"{emoji} Closed: {ticker.upper()} - {outcome.upper()}")
        if pnl is not None:
            print(f"   P&L: {pnl:+.1f}%")
        if lesson:
            print(f"   💡 Lesson: {lesson}")
    else:
        print(f"❌ No open position found for {ticker}")


def list_open():
    """List all open positions."""
    trades = load_trades()
    open_trades = [t for t in trades if t.get('status') == 'open']
    
    if not open_trades:
        print("📭 No open positions")
        return
    
    print(f"📊 Open Positions ({len(open_trades)})\n")
    
    for t in open_trades:
        direction_emoji = '📈' if t.get('direction') == 'long' else '📉'
        opened = t.get('opened', '')[:10]
        print(f"{direction_emoji} {t['ticker']} ({t.get('type', 'stock')}) — opened {opened}")
        if t.get('notes'):
            print(f"   Notes: {t['notes'][:50]}")


def show_history(days=30):
    """Show recent trade history."""
    trades = load_trades()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    
    recent = [t for t in trades if t.get('opened', '') > cutoff]
    
    if not recent:
        print(f"📭 No trades in last {days} days")
        return
    
    print(f"📜 Trade History (last {days} days)\n")
    
    for t in sorted(recent, key=lambda x: x.get('opened', ''), reverse=True):
        status = t.get('status', 'unknown')
        outcome = t.get('outcome', '')
        
        if status == 'open':
            emoji = '🔵'
            status_str = 'OPEN'
        elif outcome == 'win':
            emoji = '✅'
            status_str = f"WIN {t.get('pnl_pct', '?'):+}%" if t.get('pnl_pct') else 'WIN'
        elif outcome == 'loss':
            emoji = '❌'
            status_str = f"LOSS {t.get('pnl_pct', '?'):+}%" if t.get('pnl_pct') else 'LOSS'
        else:
            emoji = '➖'
            status_str = outcome.upper() if outcome else 'CLOSED'
        
        date = t.get('opened', '')[:10]
        print(f"{emoji} {date} | {t['ticker']:6} | {t.get('direction', 'long'):5} | {status_str}")


def show_stats():
    """Show trading statistics."""
    trades = load_trades()
    closed = [t for t in trades if t.get('status') == 'closed']
    
    if not closed:
        print("📭 No closed trades yet")
        return
    
    wins = len([t for t in closed if t.get('outcome') == 'win'])
    losses = len([t for t in closed if t.get('outcome') == 'loss'])
    breakeven = len([t for t in closed if t.get('outcome') == 'breakeven'])
    
    total = wins + losses + breakeven
    win_rate = wins / total * 100 if total > 0 else 0
    
    # P&L stats
    pnls = [t.get('pnl_pct', 0) for t in closed if t.get('pnl_pct') is not None]
    avg_pnl = sum(pnls) / len(pnls) if pnls else 0
    
    print("📊 Trading Statistics\n")
    print(f"Total trades: {total}")
    print(f"Win rate: {win_rate:.0f}% ({wins}W / {losses}L / {breakeven}BE)")
    
    if pnls:
        print(f"Average P&L: {avg_pnl:+.1f}%")
        print(f"Best trade: {max(pnls):+.1f}%")
        print(f"Worst trade: {min(pnls):+.1f}%")
    
    # Type breakdown
    print("\nBy type:")
    by_type = Counter(t.get('type', 'stock') for t in closed)
    for typ, count in by_type.most_common():
        type_trades = [t for t in closed if t.get('type') == typ]
        type_wins = len([t for t in type_trades if t.get('outcome') == 'win'])
        type_wr = type_wins / len(type_trades) * 100 if type_trades else 0
        print(f"  {typ}: {count} trades, {type_wr:.0f}% win rate")


def analyze_patterns():
    """Analyze behavioral patterns in trading."""
    trades = load_trades()
    closed = [t for t in trades if t.get('status') == 'closed']
    
    if len(closed) < 5:
        print("📭 Need at least 5 closed trades for pattern analysis")
        return
    
    print("🔍 Trading Pattern Analysis\n")
    
    # Day of week patterns
    print("**By Day of Week:**")
    by_day = {}
    for t in closed:
        day = t.get('opened_day', 'Unknown')
        if day not in by_day:
            by_day[day] = {'wins': 0, 'losses': 0}
        if t.get('outcome') == 'win':
            by_day[day]['wins'] += 1
        elif t.get('outcome') == 'loss':
            by_day[day]['losses'] += 1
    
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
        if day in by_day:
            stats = by_day[day]
            total = stats['wins'] + stats['losses']
            wr = stats['wins'] / total * 100 if total > 0 else 0
            bar = '█' * int(wr / 10)
            print(f"  {day:10} {bar:10} {wr:.0f}% ({total} trades)")
    
    # Direction patterns
    print("\n**By Direction:**")
    for direction in ['long', 'short']:
        dir_trades = [t for t in closed if t.get('direction') == direction]
        if dir_trades:
            wins = len([t for t in dir_trades if t.get('outcome') == 'win'])
            wr = wins / len(dir_trades) * 100
            print(f"  {direction.upper():6} {wr:.0f}% win rate ({len(dir_trades)} trades)")
    
    # Lessons learned
    lessons = [t.get('lesson', '') for t in closed if t.get('lesson')]
    if lessons:
        print("\n**Lessons Logged:**")
        for lesson in lessons[-5:]:
            print(f"  💡 {lesson[:60]}")
    
    # Warning signs
    print("\n**Warning Patterns:**")
    
    # Multiple trades same day
    by_date = Counter(t.get('opened', '')[:10] for t in trades)
    busy_days = [(d, c) for d, c in by_date.items() if c >= 3]
    if busy_days:
        print(f"  ⚠️  {len(busy_days)} days with 3+ trades (impulsive?)")
    
    # Losing streaks
    outcomes = [t.get('outcome') for t in sorted(closed, key=lambda x: x.get('opened', ''))]
    max_loss_streak = 0
    current_streak = 0
    for o in outcomes:
        if o == 'loss':
            current_streak += 1
            max_loss_streak = max(max_loss_streak, current_streak)
        else:
            current_streak = 0
    if max_loss_streak >= 3:
        print(f"  ⚠️  Max losing streak: {max_loss_streak}")
    
    # Option/short bias
    option_trades = [t for t in closed if t.get('type') == 'option']
    if option_trades:
        option_losses = len([t for t in option_trades if t.get('outcome') == 'loss'])
        if option_losses / len(option_trades) > 0.6:
            print(f"  ⚠️  Options losing {option_losses}/{len(option_trades)} — consider reducing")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'add' and len(sys.argv) >= 3:
        ticker = sys.argv[2]
        trade_type = 'stock'
        direction = 'long'
        notes = ''
        
        # Parse optional args
        args = sys.argv[3:]
        i = 0
        while i < len(args):
            if args[i] == '--type' and i + 1 < len(args):
                trade_type = args[i + 1]
                i += 2
            elif args[i] == '--direction' and i + 1 < len(args):
                direction = args[i + 1]
                i += 2
            elif args[i] == '--notes' and i + 1 < len(args):
                notes = args[i + 1]
                i += 2
            else:
                i += 1
        
        add_trade(ticker, trade_type, direction, notes)
    
    elif cmd == 'close' and len(sys.argv) >= 3:
        ticker = sys.argv[2]
        outcome = 'unknown'
        pnl = None
        lesson = ''
        
        args = sys.argv[3:]
        i = 0
        while i < len(args):
            if args[i] == '--outcome' and i + 1 < len(args):
                outcome = args[i + 1]
                i += 2
            elif args[i] == '--pnl' and i + 1 < len(args):
                pnl = float(args[i + 1])
                i += 2
            elif args[i] == '--lesson' and i + 1 < len(args):
                lesson = args[i + 1]
                i += 2
            else:
                i += 1
        
        close_trade(ticker, outcome, pnl, lesson)
    
    elif cmd == 'open':
        list_open()
    
    elif cmd == 'history':
        days = 30
        if len(sys.argv) >= 4 and sys.argv[2] == '--days':
            days = int(sys.argv[3])
        show_history(days)
    
    elif cmd == 'stats':
        show_stats()
    
    elif cmd == 'patterns':
        analyze_patterns()
    
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
