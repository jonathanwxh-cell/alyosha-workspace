#!/usr/bin/env python3
"""
AI Disruption Tracker
=====================

Tracks companies being disrupted by AI announcements.
Pattern: AI tool launch → incumbent stock crash → potential opportunity

Usage:
    python3 ai-disruption-tracker.py list          # Show tracked casualties
    python3 ai-disruption-tracker.py add TICKER    # Add new casualty
    python3 ai-disruption-tracker.py catalysts     # Show upcoming catalysts
"""

import json
import sys
from datetime import datetime
from pathlib import Path

WATCHLIST_FILE = Path.home() / '.openclaw/workspace/memory/watchlists/ai-disruption-casualties.json'


def load_watchlist():
    if not WATCHLIST_FILE.exists():
        return {"tickers": {}, "next_catalysts": []}
    with open(WATCHLIST_FILE) as f:
        return json.load(f)


def save_watchlist(data):
    data['last_updated'] = datetime.utcnow().isoformat() + 'Z'
    with open(WATCHLIST_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def list_casualties():
    data = load_watchlist()
    
    print(f"🎯 AI DISRUPTION CASUALTIES ({len(data['tickers'])} tracked)\n")
    print(f"Pattern: {data.get('pattern', 'N/A')}\n")
    print("-" * 60)
    
    # Sort by drop percentage
    sorted_tickers = sorted(
        data['tickers'].items(),
        key=lambda x: x[1].get('drop_pct', 0)
    )
    
    for ticker, info in sorted_tickers:
        risk_emoji = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(info.get('disruption_risk'), '⚪')
        print(f"\n{risk_emoji} {ticker}: {info.get('name')}")
        print(f"   Drop: {info.get('drop_pct')}% on {info.get('drop_date')}")
        print(f"   Sector: {info.get('sector')}")
        print(f"   Risk: {info.get('disruption_risk')}")
        if info.get('notes'):
            print(f"   Notes: {info.get('notes')}")
        if info.get('watch_for'):
            print(f"   Watch: {info.get('watch_for')}")


def show_catalysts():
    data = load_watchlist()
    
    print("📅 UPCOMING CATALYSTS\n")
    
    catalysts = sorted(data.get('next_catalysts', []), key=lambda x: x.get('date', ''))
    
    for cat in catalysts:
        print(f"  {cat.get('date')}: {cat.get('event')}")
    
    print(f"\n❓ Key Question: {data.get('key_question', 'N/A')}")


def add_casualty(ticker):
    data = load_watchlist()
    
    print(f"Adding {ticker} to AI disruption watchlist...")
    
    name = input("Company name: ").strip()
    sector = input("Sector: ").strip()
    drop_pct = float(input("Drop %: ").strip())
    risk = input("Risk (HIGH/MEDIUM/LOW): ").strip().upper()
    notes = input("Notes: ").strip()
    
    data['tickers'][ticker] = {
        'name': name,
        'sector': sector,
        'drop_date': datetime.utcnow().strftime('%Y-%m-%d'),
        'drop_pct': drop_pct,
        'disruption_risk': risk,
        'notes': notes,
        'watch_for': ''
    }
    
    save_watchlist(data)
    print(f"✅ Added {ticker}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'list':
        list_casualties()
    elif cmd == 'catalysts':
        show_catalysts()
    elif cmd == 'add' and len(sys.argv) >= 3:
        add_casualty(sys.argv[2].upper())
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
