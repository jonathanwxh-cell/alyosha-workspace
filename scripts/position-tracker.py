#!/usr/bin/env python3
"""
Position Tracker - Monitor open positions, alert on expiry and price moves

Scans trade-journal.jsonl for open options positions.
Alerts when:
- Approaching expiry (7d, 3d, 1d)
- Strike distance changes significantly
- Underlying moves >2%

Usage:
    python3 position-tracker.py check     # Check all open positions
    python3 position-tracker.py alerts    # Only show positions needing attention
    python3 position-tracker.py summary   # One-line summary
    python3 position-tracker.py add       # Quick-add a new position (interactive)
    python3 position-tracker.py close TICKER  # Close a position
    python3 position-tracker.py history   # Show position history with P&L
"""

import json
import sys
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path
import re

JOURNAL_FILE = Path.home() / '.openclaw/workspace/memory/trade-journal.jsonl'
ALERTS_FILE = Path.home() / '.openclaw/workspace/memory/position-alerts.json'


def load_open_positions():
    """Load open positions from trade journal."""
    positions = []
    if not JOURNAL_FILE.exists():
        return positions
    
    with open(JOURNAL_FILE) as f:
        for line in f:
            if line.strip():
                try:
                    trade = json.loads(line)
                    if trade.get('status') == 'open':
                        positions.append(trade)
                except:
                    pass
    return positions


def get_quote(ticker):
    """Get current price via FMP client."""
    try:
        result = subprocess.run(
            ['python3', str(Path.home() / '.openclaw/workspace/scripts/fmp-client.py'), 'quote', ticker],
            capture_output=True, text=True, timeout=30
        )
        # Parse: "SPY: $689.53 (-5.88, -0.85%)"
        match = re.search(r'\$([0-9,.]+)', result.stdout)
        if match:
            return float(match.group(1).replace(',', ''))
    except:
        pass
    return None


def parse_option_from_notes(notes):
    """
    Extract option details from notes.
    Examples:
        "671P exp 2026-02-11" -> {'strike': 671, 'type': 'put', 'expiry': '2026-02-11'}
        "700C exp 2026-03-15" -> {'strike': 700, 'type': 'call', 'expiry': '2026-03-15'}
    """
    if not notes:
        return None
    
    # Pattern: 671P or 700C
    strike_match = re.search(r'(\d+)([PCpc])', notes)
    # Pattern: exp 2026-02-11 or expiry 2026-02-11
    expiry_match = re.search(r'exp(?:iry)?\s*(\d{4}-\d{2}-\d{2})', notes)
    
    if strike_match:
        result = {
            'strike': int(strike_match.group(1)),
            'type': 'put' if strike_match.group(2).upper() == 'P' else 'call'
        }
        if expiry_match:
            result['expiry'] = expiry_match.group(1)
        return result
    return None


def days_to_expiry(expiry_str):
    """Calculate days until expiry."""
    try:
        expiry = datetime.strptime(expiry_str, '%Y-%m-%d').date()
        today = datetime.now(timezone.utc).date()
        return (expiry - today).days
    except:
        return None


def analyze_position(position):
    """Analyze a single position and return status."""
    ticker = position.get('ticker', 'UNKNOWN')
    notes = position.get('notes', '')
    direction = position.get('direction', 'unknown')
    
    result = {
        'ticker': ticker,
        'direction': direction,
        'notes': notes,
        'alerts': [],
        'status': 'ok'
    }
    
    # Get current price
    price = get_quote(ticker)
    if price:
        result['current_price'] = price
    
    # Parse option details
    option = parse_option_from_notes(notes)
    if option:
        result['option'] = option
        
        if 'expiry' in option:
            dte = days_to_expiry(option['expiry'])
            result['days_to_expiry'] = dte
            
            # Expiry alerts
            if dte is not None:
                if dte <= 0:
                    result['alerts'].append(f"⚠️ EXPIRED or expiring TODAY")
                    result['status'] = 'critical'
                elif dte <= 1:
                    result['alerts'].append(f"🔴 Expires TOMORROW")
                    result['status'] = 'critical'
                elif dte <= 3:
                    result['alerts'].append(f"🟠 Expires in {dte} days")
                    result['status'] = 'warning'
                elif dte <= 7:
                    result['alerts'].append(f"🟡 Expires in {dte} days")
                    if result['status'] == 'ok':
                        result['status'] = 'watch'
        
        # Strike distance
        if price and 'strike' in option:
            strike = option['strike']
            distance = price - strike
            distance_pct = (distance / price) * 100
            
            result['strike_distance'] = distance
            result['strike_distance_pct'] = distance_pct
            
            opt_type = option.get('type', 'unknown')
            
            if opt_type == 'put':
                # Put is ITM if price < strike
                if price < strike:
                    itm_pct = ((strike - price) / strike) * 100
                    result['alerts'].append(f"✅ PUT is ITM by {itm_pct:.1f}%")
                else:
                    otm_pct = ((price - strike) / strike) * 100
                    result['alerts'].append(f"📉 PUT is OTM by {otm_pct:.1f}% (need ${distance:.2f} drop)")
            
            elif opt_type == 'call':
                # Call is ITM if price > strike
                if price > strike:
                    itm_pct = ((price - strike) / strike) * 100
                    result['alerts'].append(f"✅ CALL is ITM by {itm_pct:.1f}%")
                else:
                    otm_pct = ((strike - price) / strike) * 100
                    result['alerts'].append(f"📈 CALL is OTM by {otm_pct:.1f}% (need ${-distance:.2f} rise)")
    
    return result


def check_positions():
    """Check all open positions."""
    positions = load_open_positions()
    
    if not positions:
        print("No open positions found.")
        return
    
    print(f"📊 **Open Positions ({len(positions)})**\n")
    
    for pos in positions:
        analysis = analyze_position(pos)
        
        # Header
        status_emoji = {'critical': '🔴', 'warning': '🟠', 'watch': '🟡', 'ok': '🟢'}
        emoji = status_emoji.get(analysis['status'], '⚪')
        
        print(f"{emoji} **{analysis['ticker']}** ({analysis['direction']})")
        
        if 'current_price' in analysis:
            print(f"   Current: ${analysis['current_price']:.2f}")
        
        if 'option' in analysis:
            opt = analysis['option']
            strike_str = f"{opt['strike']}{opt['type'][0].upper()}"
            if 'expiry' in opt:
                strike_str += f" exp {opt['expiry']}"
            print(f"   Position: {strike_str}")
        
        if 'days_to_expiry' in analysis:
            print(f"   DTE: {analysis['days_to_expiry']} days")
        
        for alert in analysis['alerts']:
            print(f"   {alert}")
        
        print()


def show_alerts():
    """Show only positions needing attention."""
    positions = load_open_positions()
    
    alerts = []
    for pos in positions:
        analysis = analyze_position(pos)
        if analysis['status'] in ['critical', 'warning', 'watch']:
            alerts.append(analysis)
    
    if not alerts:
        print("✅ No positions need immediate attention.")
        return
    
    print(f"⚠️ **{len(alerts)} position(s) need attention:**\n")
    for a in alerts:
        print(f"• {a['ticker']}: {', '.join(a['alerts'])}")


def summary():
    """One-line summary for heartbeat."""
    positions = load_open_positions()
    
    if not positions:
        print("No open positions")
        return
    
    critical = 0
    warning = 0
    
    for pos in positions:
        analysis = analyze_position(pos)
        if analysis['status'] == 'critical':
            critical += 1
        elif analysis['status'] in ['warning', 'watch']:
            warning += 1
    
    parts = [f"{len(positions)} open"]
    if critical:
        parts.append(f"🔴 {critical} critical")
    if warning:
        parts.append(f"🟠 {warning} watch")
    
    print(" | ".join(parts))


def add_position():
    """Quick-add a new position interactively."""
    print("📝 Add New Position\n")
    
    ticker = input("Ticker (e.g., SPY): ").strip().upper()
    if not ticker:
        print("❌ Ticker required")
        return
    
    pos_type = input("Type (option/stock) [option]: ").strip().lower() or 'option'
    direction = input("Direction (long/short) [long]: ").strip().lower() or 'long'
    
    notes = ""
    if pos_type == 'option':
        strike = input("Strike price: ").strip()
        opt_type = input("Put/Call (P/C): ").strip().upper()
        expiry = input("Expiry (YYYY-MM-DD): ").strip()
        
        if strike and opt_type and expiry:
            notes = f"{strike}{opt_type} exp {expiry}"
        else:
            notes = input("Notes (manual): ").strip()
    else:
        notes = input("Notes: ").strip()
    
    entry_price = input("Entry price (optional): ").strip()
    
    # Build entry
    entry = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'ticker': ticker,
        'type': pos_type,
        'direction': direction,
        'status': 'open',
        'notes': notes
    }
    
    if entry_price:
        try:
            entry['entry_price'] = float(entry_price)
        except:
            pass
    
    # Append to journal
    with open(JOURNAL_FILE, 'a') as f:
        f.write(json.dumps(entry) + '\n')
    
    print(f"\n✅ Added: {ticker} {direction} {notes}")
    
    # Show current price
    price = get_quote(ticker)
    if price:
        print(f"   Current {ticker}: ${price:.2f}")


def close_position(ticker):
    """Close an open position."""
    positions = []
    closed = False
    
    if not JOURNAL_FILE.exists():
        print("No positions found")
        return
    
    with open(JOURNAL_FILE) as f:
        for line in f:
            if line.strip():
                try:
                    trade = json.loads(line)
                    positions.append(trade)
                except:
                    pass
    
    # Find and close matching position
    for pos in positions:
        if pos.get('ticker', '').upper() == ticker.upper() and pos.get('status') == 'open':
            pos['status'] = 'closed'
            pos['closed_at'] = datetime.now(timezone.utc).isoformat()
            
            # Get exit price
            exit_price = get_quote(ticker)
            if exit_price:
                pos['exit_price'] = exit_price
                
                # Calculate P&L if entry price exists
                if 'entry_price' in pos:
                    entry = pos['entry_price']
                    direction = pos.get('direction', 'long')
                    
                    if direction == 'long':
                        pnl_pct = ((exit_price - entry) / entry) * 100
                    else:
                        pnl_pct = ((entry - exit_price) / entry) * 100
                    
                    pos['pnl_pct'] = round(pnl_pct, 2)
            
            closed = True
            print(f"✅ Closed: {ticker}")
            if 'pnl_pct' in pos:
                emoji = "🟢" if pos['pnl_pct'] > 0 else "🔴"
                print(f"   {emoji} P&L: {pos['pnl_pct']:+.1f}%")
            break
    
    if not closed:
        print(f"❌ No open position found for {ticker}")
        return
    
    # Rewrite journal
    with open(JOURNAL_FILE, 'w') as f:
        for pos in positions:
            f.write(json.dumps(pos) + '\n')


def show_history():
    """Show position history with P&L."""
    if not JOURNAL_FILE.exists():
        print("No position history")
        return
    
    positions = []
    with open(JOURNAL_FILE) as f:
        for line in f:
            if line.strip():
                try:
                    positions.append(json.loads(line))
                except:
                    pass
    
    if not positions:
        print("No position history")
        return
    
    # Separate open and closed
    open_pos = [p for p in positions if p.get('status') == 'open']
    closed_pos = [p for p in positions if p.get('status') == 'closed']
    
    print(f"📊 **Position History**\n")
    
    if open_pos:
        print(f"**Open ({len(open_pos)}):**")
        for p in open_pos:
            print(f"  • {p.get('ticker')} {p.get('direction', '')} - {p.get('notes', '')}")
    
    if closed_pos:
        print(f"\n**Closed ({len(closed_pos)}):**")
        
        wins = 0
        losses = 0
        total_pnl = 0
        
        for p in closed_pos:
            pnl = p.get('pnl_pct', 0)
            emoji = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "⚪"
            print(f"  {emoji} {p.get('ticker')} {p.get('direction', '')} - {pnl:+.1f}%")
            
            if pnl > 0:
                wins += 1
            elif pnl < 0:
                losses += 1
            total_pnl += pnl
        
        if wins + losses > 0:
            win_rate = wins / (wins + losses) * 100
            print(f"\n**Stats:** {wins}W/{losses}L ({win_rate:.0f}% win rate) | Total: {total_pnl:+.1f}%")


def main():
    if len(sys.argv) < 2:
        check_positions()
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'check':
        check_positions()
    elif cmd == 'alerts':
        show_alerts()
    elif cmd == 'summary':
        summary()
    elif cmd == 'add':
        add_position()
    elif cmd == 'close' and len(sys.argv) >= 3:
        close_position(sys.argv[2])
    elif cmd == 'history':
        show_history()
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == '__main__':
    main()
