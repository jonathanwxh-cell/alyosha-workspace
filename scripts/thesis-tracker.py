#!/usr/bin/env python3
"""
Investment Thesis Tracker
=========================

Track investment theses, what would change your view, and learn from outcomes.

Usage:
    python3 thesis-tracker.py add TICKER           # Interactive add
    python3 thesis-tracker.py add TICKER --quick "thesis" --conviction 7
    python3 thesis-tracker.py list                 # All active theses
    python3 thesis-tracker.py show TICKER          # Detail on one thesis
    python3 thesis-tracker.py check                # Check all for trigger conditions
    python3 thesis-tracker.py close TICKER         # Close and record outcome
    python3 thesis-tracker.py review               # Learning review
    python3 thesis-tracker.py remind               # Theses needing review (>30 days)

Key insight: The value isn't tracking price - it's tracking YOUR REASONING
so you can learn from it later.
"""

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
import os
import urllib.request

THESIS_FILE = Path.home() / '.openclaw/workspace/memory/investment-theses.json'
OUTCOMES_FILE = Path.home() / '.openclaw/workspace/memory/thesis-outcomes.jsonl'
FMP_ENV = Path.home() / '.secure/fmp.env'

def load_theses() -> dict:
    """Load theses from file."""
    if THESIS_FILE.exists():
        return json.loads(THESIS_FILE.read_text())
    return {"theses": {}, "meta": {"created": datetime.now(timezone.utc).isoformat()}}

def save_theses(data: dict):
    """Save theses to file."""
    THESIS_FILE.parent.mkdir(parents=True, exist_ok=True)
    THESIS_FILE.write_text(json.dumps(data, indent=2))

def get_fmp_key() -> str:
    """Get FMP API key."""
    if FMP_ENV.exists():
        for line in FMP_ENV.read_text().split('\n'):
            if line.startswith('FMP_API_KEY='):
                return line.split('=', 1)[1].strip().strip('"\'')
    return os.environ.get('FMP_API_KEY', '')

def get_quote(symbol: str) -> dict:
    """Get current quote from FMP."""
    key = get_fmp_key()
    if not key:
        return {}
    try:
        url = f"https://financialmodelingprep.com/stable/quote?symbol={symbol}&apikey={key}"
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
            return data[0] if data else {}
    except Exception as e:
        return {"error": str(e)}

def add_thesis(symbol: str, quick: str = None, conviction: int = None):
    """Add a new thesis."""
    symbol = symbol.upper()
    data = load_theses()
    
    if symbol in data["theses"]:
        print(f"⚠️  Thesis for {symbol} already exists. Use 'update' to modify.")
        return
    
    # Get current price for reference
    quote = get_quote(symbol)
    current_price = quote.get('price', 'N/A')
    
    if quick:
        # Quick mode - minimal input
        thesis = {
            "symbol": symbol,
            "thesis": quick,
            "conviction": conviction or 5,
            "direction": "long",  # default
            "timeframe": "medium",  # default
            "entry_price": current_price,
            "created": datetime.now(timezone.utc).isoformat(),
            "updated": datetime.now(timezone.utc).isoformat(),
            "would_change_view": [],
            "status": "active"
        }
    else:
        # Interactive mode
        print(f"\n📊 Adding thesis for {symbol}")
        print(f"   Current price: ${current_price}\n")
        
        thesis_text = input("Thesis (why you like/dislike it): ").strip()
        if not thesis_text:
            print("Thesis required.")
            return
            
        direction = input("Direction [long/short/neutral] (default: long): ").strip().lower()
        if direction not in ['long', 'short', 'neutral']:
            direction = 'long'
            
        timeframe = input("Timeframe [short/medium/long] (default: medium): ").strip().lower()
        if timeframe not in ['short', 'medium', 'long']:
            timeframe = 'medium'
        
        conv = input("Conviction 1-10 (default: 5): ").strip()
        try:
            conviction = int(conv) if conv else 5
            conviction = max(1, min(10, conviction))
        except:
            conviction = 5
        
        # The key question
        print("\n❓ What would change your view? (one per line, empty to finish)")
        changes = []
        while True:
            change = input("  → ").strip()
            if not change:
                break
            changes.append(change)
        
        thesis = {
            "symbol": symbol,
            "thesis": thesis_text,
            "conviction": conviction,
            "direction": direction,
            "timeframe": timeframe,
            "entry_price": current_price,
            "created": datetime.now(timezone.utc).isoformat(),
            "updated": datetime.now(timezone.utc).isoformat(),
            "would_change_view": changes,
            "status": "active"
        }
    
    data["theses"][symbol] = thesis
    save_theses(data)
    
    print(f"\n✅ Thesis added for {symbol}")
    print(f"   Direction: {thesis['direction']} | Conviction: {thesis['conviction']}/10")
    print(f"   Entry: ${current_price}")

def list_theses():
    """List all active theses."""
    data = load_theses()
    theses = data.get("theses", {})
    
    if not theses:
        print("📋 No active theses. Add one with: thesis-tracker.py add TICKER")
        return
    
    active = [(s, t) for s, t in theses.items() if t.get("status") == "active"]
    closed = [(s, t) for s, t in theses.items() if t.get("status") != "active"]
    
    if active:
        print("\n📊 Active Theses\n")
        print(f"{'Ticker':<8} {'Dir':<6} {'Conv':<5} {'Entry':<10} {'Thesis':<40}")
        print("-" * 75)
        
        for symbol, thesis in sorted(active, key=lambda x: -x[1].get('conviction', 5)):
            entry = thesis.get('entry_price', 'N/A')
            entry_str = f"${entry:.2f}" if isinstance(entry, (int, float)) else str(entry)
            thesis_short = thesis.get('thesis', '')[:38]
            print(f"{symbol:<8} {thesis['direction']:<6} {thesis['conviction']}/10   {entry_str:<10} {thesis_short}")
    
    if closed:
        print(f"\n📁 {len(closed)} closed thesis(es). Use 'review' to see outcomes.")

def show_thesis(symbol: str):
    """Show detailed thesis."""
    symbol = symbol.upper()
    data = load_theses()
    
    if symbol not in data.get("theses", {}):
        print(f"❌ No thesis found for {symbol}")
        return
    
    thesis = data["theses"][symbol]
    quote = get_quote(symbol)
    current_price = quote.get('price', 'N/A')
    
    # Calculate return if possible
    entry = thesis.get('entry_price')
    if isinstance(entry, (int, float)) and isinstance(current_price, (int, float)):
        ret = ((current_price - entry) / entry) * 100
        if thesis.get('direction') == 'short':
            ret = -ret
        ret_str = f"{'+' if ret >= 0 else ''}{ret:.1f}%"
    else:
        ret_str = "N/A"
    
    print(f"\n{'='*60}")
    print(f"📊 {symbol} Thesis")
    print(f"{'='*60}")
    print(f"\nStatus: {thesis.get('status', 'active').upper()}")
    print(f"Direction: {thesis.get('direction', 'long')} | Conviction: {thesis.get('conviction', 5)}/10")
    print(f"Timeframe: {thesis.get('timeframe', 'medium')}")
    print(f"\nEntry: ${entry}  →  Current: ${current_price}  ({ret_str})")
    print(f"\n📝 Thesis:\n   {thesis.get('thesis', 'N/A')}")
    
    changes = thesis.get('would_change_view', [])
    if changes:
        print(f"\n❓ Would change view if:")
        for change in changes:
            print(f"   • {change}")
    
    created = thesis.get('created', '')[:10]
    updated = thesis.get('updated', '')[:10]
    print(f"\nCreated: {created} | Updated: {updated}")
    print(f"{'='*60}\n")

def check_theses():
    """Check all theses for review triggers."""
    data = load_theses()
    theses = data.get("theses", {})
    
    if not theses:
        print("No theses to check.")
        return
    
    print("\n🔍 Thesis Check\n")
    
    alerts = []
    
    for symbol, thesis in theses.items():
        if thesis.get('status') != 'active':
            continue
            
        quote = get_quote(symbol)
        current_price = quote.get('price')
        entry = thesis.get('entry_price')
        
        if not isinstance(current_price, (int, float)) or not isinstance(entry, (int, float)):
            continue
        
        # Calculate return
        ret = ((current_price - entry) / entry) * 100
        if thesis.get('direction') == 'short':
            ret = -ret
        
        # Trigger conditions
        triggers = []
        
        # Big move (>15% either direction)
        if abs(ret) > 15:
            triggers.append(f"{'🟢' if ret > 0 else '🔴'} {'+' if ret >= 0 else ''}{ret:.1f}% since entry")
        
        # Conviction vs performance mismatch
        if thesis.get('conviction', 5) >= 7 and ret < -10:
            triggers.append(f"⚠️  High conviction ({thesis['conviction']}/10) but down {ret:.1f}%")
        
        # Stale thesis (>30 days)
        updated = thesis.get('updated', thesis.get('created', ''))
        if updated:
            try:
                update_date = datetime.fromisoformat(updated.replace('Z', '+00:00'))
                age = (datetime.now(timezone.utc) - update_date).days
                if age > 30:
                    triggers.append(f"📅 {age} days since last update")
            except:
                pass
        
        if triggers:
            alerts.append((symbol, thesis, ret, triggers))
    
    if alerts:
        for symbol, thesis, ret, triggers in alerts:
            print(f"📊 {symbol} ({thesis.get('direction', 'long')}, {thesis.get('conviction', 5)}/10)")
            for trigger in triggers:
                print(f"   {trigger}")
            print()
        
        print("💡 Tip: Review these with 'show TICKER' and update or close if thesis changed.")
    else:
        print("✅ All theses look stable. No alerts.")

def close_thesis(symbol: str):
    """Close a thesis and record outcome."""
    symbol = symbol.upper()
    data = load_theses()
    
    if symbol not in data.get("theses", {}):
        print(f"❌ No thesis found for {symbol}")
        return
    
    thesis = data["theses"][symbol]
    quote = get_quote(symbol)
    exit_price = quote.get('price', 'N/A')
    entry = thesis.get('entry_price')
    
    # Calculate return
    if isinstance(exit_price, (int, float)) and isinstance(entry, (int, float)):
        ret = ((exit_price - entry) / entry) * 100
        if thesis.get('direction') == 'short':
            ret = -ret
    else:
        ret = None
    
    print(f"\n📊 Closing thesis for {symbol}")
    print(f"   Entry: ${entry} → Exit: ${exit_price}")
    if ret is not None:
        print(f"   Return: {'+' if ret >= 0 else ''}{ret:.1f}%")
    
    outcome = input("\nOutcome [win/loss/scratch/abandoned]: ").strip().lower()
    if outcome not in ['win', 'loss', 'scratch', 'abandoned']:
        outcome = 'scratch'
    
    lesson = input("What did you learn? ").strip()
    
    # Update thesis
    thesis["status"] = "closed"
    thesis["closed"] = datetime.now(timezone.utc).isoformat()
    thesis["exit_price"] = exit_price
    thesis["outcome"] = outcome
    thesis["return_pct"] = ret
    thesis["lesson"] = lesson
    
    data["theses"][symbol] = thesis
    save_theses(data)
    
    # Log to outcomes file
    outcome_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "symbol": symbol,
        "direction": thesis.get("direction"),
        "conviction": thesis.get("conviction"),
        "thesis": thesis.get("thesis"),
        "entry_price": entry,
        "exit_price": exit_price,
        "return_pct": ret,
        "outcome": outcome,
        "lesson": lesson,
        "held_days": None  # Calculate if needed
    }
    
    try:
        created = datetime.fromisoformat(thesis.get('created', '').replace('Z', '+00:00'))
        outcome_entry["held_days"] = (datetime.now(timezone.utc) - created).days
    except:
        pass
    
    with open(OUTCOMES_FILE, 'a') as f:
        f.write(json.dumps(outcome_entry) + '\n')
    
    print(f"\n✅ Thesis closed. Outcome: {outcome}")
    if lesson:
        print(f"   Lesson: {lesson}")

def review_outcomes():
    """Review past outcomes for learning."""
    if not OUTCOMES_FILE.exists():
        print("📋 No closed theses yet.")
        return
    
    outcomes = []
    with open(OUTCOMES_FILE) as f:
        for line in f:
            if line.strip():
                outcomes.append(json.loads(line))
    
    if not outcomes:
        print("📋 No closed theses yet.")
        return
    
    wins = [o for o in outcomes if o.get('outcome') == 'win']
    losses = [o for o in outcomes if o.get('outcome') == 'loss']
    scratches = [o for o in outcomes if o.get('outcome') in ['scratch', 'abandoned']]
    
    print("\n📊 Thesis Outcomes Review")
    print("=" * 50)
    print(f"\nTotal: {len(outcomes)} | Wins: {len(wins)} | Losses: {len(losses)} | Scratch: {len(scratches)}")
    
    if wins or losses:
        win_rate = len(wins) / (len(wins) + len(losses)) * 100
        print(f"Win Rate: {win_rate:.0f}%")
    
    # Average return
    returns = [o.get('return_pct') for o in outcomes if o.get('return_pct') is not None]
    if returns:
        avg_return = sum(returns) / len(returns)
        print(f"Avg Return: {'+' if avg_return >= 0 else ''}{avg_return:.1f}%")
    
    # Lessons learned
    lessons = [o.get('lesson') for o in outcomes if o.get('lesson')]
    if lessons:
        print(f"\n📚 Lessons Learned:")
        for i, lesson in enumerate(lessons[-5:], 1):  # Last 5
            print(f"   {i}. {lesson}")
    
    # High conviction outcomes
    high_conv = [o for o in outcomes if o.get('conviction', 5) >= 7]
    if high_conv:
        hc_wins = sum(1 for o in high_conv if o.get('outcome') == 'win')
        print(f"\n🎯 High Conviction (7+): {hc_wins}/{len(high_conv)} wins ({hc_wins/len(high_conv)*100:.0f}%)")
    
    print()

def remind_stale():
    """Find theses that need review."""
    data = load_theses()
    theses = data.get("theses", {})
    
    stale = []
    for symbol, thesis in theses.items():
        if thesis.get('status') != 'active':
            continue
        
        updated = thesis.get('updated', thesis.get('created', ''))
        if updated:
            try:
                update_date = datetime.fromisoformat(updated.replace('Z', '+00:00'))
                age = (datetime.now(timezone.utc) - update_date).days
                if age > 30:
                    stale.append((symbol, thesis, age))
            except:
                pass
    
    if stale:
        print("\n⏰ Theses needing review (>30 days old):\n")
        for symbol, thesis, age in sorted(stale, key=lambda x: -x[2]):
            print(f"   {symbol}: {age} days (conviction: {thesis.get('conviction', 5)}/10)")
        print(f"\nUpdate with 'show TICKER' then edit, or 'close TICKER' if done.")
    else:
        print("✅ All theses up to date.")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'add':
        if len(sys.argv) < 3:
            print("Usage: thesis-tracker.py add TICKER [--quick 'thesis'] [--conviction N]")
            return
        symbol = sys.argv[2]
        
        # Check for quick mode
        quick = None
        conviction = None
        args = sys.argv[3:]
        i = 0
        while i < len(args):
            if args[i] == '--quick' and i + 1 < len(args):
                quick = args[i + 1]
                i += 2
            elif args[i] == '--conviction' and i + 1 < len(args):
                try:
                    conviction = int(args[i + 1])
                except:
                    pass
                i += 2
            else:
                i += 1
        
        add_thesis(symbol, quick, conviction)
    
    elif cmd == 'list':
        list_theses()
    
    elif cmd == 'show':
        if len(sys.argv) < 3:
            print("Usage: thesis-tracker.py show TICKER")
            return
        show_thesis(sys.argv[2])
    
    elif cmd == 'check':
        check_theses()
    
    elif cmd == 'close':
        if len(sys.argv) < 3:
            print("Usage: thesis-tracker.py close TICKER")
            return
        close_thesis(sys.argv[2])
    
    elif cmd == 'review':
        review_outcomes()
    
    elif cmd == 'remind':
        remind_stale()
    
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)

if __name__ == "__main__":
    main()
