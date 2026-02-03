#!/usr/bin/env python3
"""
ASCII Sparkline Generator
=========================

Generate tiny text-based charts for stock performance.
Works in Telegram, terminals, anywhere text works.

Usage:
    python3 sparkline.py NVDA           # 30-day sparkline
    python3 sparkline.py NVDA --days 7  # 7-day sparkline
    python3 sparkline.py NVDA AMD TSM   # Multiple stocks
    python3 sparkline.py --watchlist    # All watchlist stocks
"""

import json
import urllib.request
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Sparkline characters (8 levels)
SPARKS = ' ▁▂▃▄▅▆█'

# Alternative block style
BLOCKS = '▏▎▍▌▋▊▉█'

# Trend arrows
TREND_UP = '↗'
TREND_DOWN = '↘'
TREND_FLAT = '→'

ENV_FILE = Path.home() / '.secure/fmp.env'

def get_api_key() -> str:
    """Load FMP API key."""
    key = os.environ.get('FMP_API_KEY')
    if key:
        return key
    if ENV_FILE.exists():
        with open(ENV_FILE) as f:
            for line in f:
                if line.startswith('FMP_API_KEY='):
                    return line.split('=', 1)[1].strip()
    raise ValueError("FMP_API_KEY not found")


def get_historical(symbol: str, days: int = 30) -> list:
    """Fetch historical daily prices using stable API."""
    api_key = get_api_key()
    # Use stable API endpoint
    url = f"https://financialmodelingprep.com/stable/historical-price-eod/light?symbol={symbol}&apikey={api_key}"
    
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            if isinstance(data, list) and data:
                # Data comes newest first, take N days and reverse to chronological
                recent = data[:days]
                return [{'close': d['price'], 'date': d['date']} for d in reversed(recent)]
    except Exception as e:
        pass
    return []


def normalize(values: list, levels: int = 8) -> list:
    """Normalize values to 0-7 range for sparkline."""
    if not values:
        return []
    
    min_val = min(values)
    max_val = max(values)
    range_val = max_val - min_val
    
    if range_val == 0:
        return [levels // 2] * len(values)
    
    return [int((v - min_val) / range_val * (levels - 1)) for v in values]


def make_sparkline(prices: list, chars: str = SPARKS) -> str:
    """Convert prices to sparkline string."""
    if not prices:
        return "No data"
    
    levels = normalize(prices)
    return ''.join(chars[l] for l in levels)


def get_trend(prices: list) -> tuple:
    """Calculate trend direction and percentage."""
    if len(prices) < 2:
        return TREND_FLAT, 0.0
    
    start = prices[0]
    end = prices[-1]
    pct = ((end - start) / start) * 100
    
    if pct > 1:
        return TREND_UP, pct
    elif pct < -1:
        return TREND_DOWN, pct
    else:
        return TREND_FLAT, pct


def format_sparkline(symbol: str, days: int = 30) -> str:
    """Generate formatted sparkline for a symbol."""
    hist = get_historical(symbol, days)
    if not hist:
        return f"{symbol}: ❌ No data"
    
    prices = [d['close'] for d in hist]
    spark = make_sparkline(prices)
    trend, pct = get_trend(prices)
    
    current = prices[-1]
    sign = '+' if pct >= 0 else ''
    
    return f"{symbol} ${current:.0f} {spark} {trend}{sign}{pct:.1f}%"


def format_mini(symbol: str, days: int = 14) -> str:
    """Ultra-compact sparkline."""
    hist = get_historical(symbol, days)
    if not hist:
        return f"{symbol}:?"
    
    prices = [d['close'] for d in hist]
    spark = make_sparkline(prices)
    trend, pct = get_trend(prices)
    sign = '+' if pct >= 0 else ''
    
    return f"{symbol}{spark}{sign}{pct:.0f}%"


def watchlist_sparklines(days: int = 30) -> str:
    """Generate sparklines for watchlist."""
    watchlist = ['NVDA', 'AMD', 'SMCI', 'TSM', 'AVGO']
    lines = [f"📈 **{days}-Day Trends**\n"]
    
    for symbol in watchlist:
        lines.append(format_sparkline(symbol, days))
    
    return '\n'.join(lines)


def compare_view(symbols: list, days: int = 30) -> str:
    """Side-by-side comparison."""
    lines = [f"📊 **{days}-Day Comparison**\n"]
    lines.append("```")
    
    for symbol in symbols:
        lines.append(format_sparkline(symbol, days))
    
    lines.append("```")
    return '\n'.join(lines)


def main():
    args = sys.argv[1:]
    
    if not args:
        print("Usage: sparkline.py SYMBOL [--days N] [--mini]")
        return
    
    days = 30
    mini = False
    watchlist = False
    symbols = []
    
    i = 0
    while i < len(args):
        if args[i] == '--days' and i + 1 < len(args):
            days = int(args[i + 1])
            i += 2
        elif args[i] == '--mini':
            mini = True
            i += 1
        elif args[i] == '--watchlist':
            watchlist = True
            i += 1
        else:
            symbols.append(args[i].upper())
            i += 1
    
    if watchlist:
        print(watchlist_sparklines(days))
    elif len(symbols) > 1:
        print(compare_view(symbols, days))
    elif symbols:
        if mini:
            print(format_mini(symbols[0], days))
        else:
            print(format_sparkline(symbols[0], days))
    else:
        print(watchlist_sparklines(days))


if __name__ == "__main__":
    main()
