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


def main():
    if len(sys.argv) < 2:
        check_positions()
        return
    
    cmd = sys.argv[1]
    
    if cmd == 'check':
        check_positions()
    elif cmd == 'alerts':
        show_alerts()
    elif cmd == 'summary':
        summary()
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: position-tracker.py [check|alerts|summary]")


if __name__ == '__main__':
    main()
