#!/usr/bin/env python3
"""
Watchlist Morning Snapshot
==========================

Quick pre-market glance at watched stocks.
Runs ~20:30 SGT (8:30 AM EST pre-market).

Shows:
- Overnight price changes
- Pre-market moves (if available)
- Volume alerts
- Brief news headlines

Usage:
    python3 watchlist-snapshot.py           # Full snapshot
    python3 watchlist-snapshot.py --brief   # One-liner per stock
    python3 watchlist-snapshot.py --edit    # Show watchlist config
"""

import json
import urllib.request
import urllib.error
import sys
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

# =============================================================================
# Configuration
# =============================================================================

# Watchlist - edit as needed
WATCHLIST = [
    {"symbol": "NVDA", "name": "NVIDIA", "notes": "Core holding, AI leader"},
    {"symbol": "AMD", "name": "AMD", "notes": "Competitor watch"},
    {"symbol": "SMCI", "name": "Super Micro", "notes": "AI infrastructure"},
    {"symbol": "TSM", "name": "TSMC", "notes": "Foundry exposure"},
    {"symbol": "AVGO", "name": "Broadcom", "notes": "AI networking"},
]

# Paths
MEMORY_DIR = Path.home() / '.openclaw/workspace/memory'
ENV_FILE = Path.home() / '.secure/fmp.env'

# =============================================================================
# FMP API (direct)
# =============================================================================

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


def fmp_request(endpoint: str, params: dict = None) -> any:
    """Make FMP API request."""
    api_key = get_api_key()
    params = params or {}
    params['apikey'] = api_key
    
    query = '&'.join(f"{k}={v}" for k, v in params.items())
    url = f"https://financialmodelingprep.com/stable/{endpoint}?{query}"
    
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        return {"error": str(e)}


def get_quotes(symbols: list) -> dict:
    """Get batch quotes for multiple symbols."""
    results = {}
    
    # FMP stable API needs individual requests
    for symbol in symbols:
        data = fmp_request("quote", {"symbol": symbol})
        if isinstance(data, list) and data:
            results[symbol] = data[0]
        elif isinstance(data, dict) and 'symbol' in data:
            results[symbol] = data
    
    return results


def get_news(symbol: str, limit: int = 2) -> list:
    """Get recent news for a symbol (using v3 API)."""
    try:
        api_key = get_api_key()
        # News is on v3 API, not stable
        url = f"https://financialmodelingprep.com/api/v3/stock_news?tickers={symbol}&limit={limit}&apikey={api_key}"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            if isinstance(data, list):
                return data[:limit]
    except:
        pass
    return []


# =============================================================================
# Formatting
# =============================================================================

def format_change(change: float, pct: float) -> str:
    """Format price change with emoji."""
    if pct > 3:
        emoji = "🚀"
    elif pct > 1:
        emoji = "📈"
    elif pct > 0:
        emoji = "↗️"
    elif pct > -1:
        emoji = "↘️"
    elif pct > -3:
        emoji = "📉"
    else:
        emoji = "💥"
    
    sign = "+" if change >= 0 else ""
    return f"{emoji} {sign}{change:.2f} ({sign}{pct:.1f}%)"


def get_market_status() -> str:
    """Determine market status based on time."""
    now = datetime.now(timezone.utc)
    # EST is UTC-5 (standard) or UTC-4 (DST)
    est_hour = (now.hour - 5) % 24
    est_minute = now.minute
    
    # Pre-market: 4:00-9:30 EST
    if 4 <= est_hour < 9 or (est_hour == 9 and est_minute < 30):
        return "🌅 pre-market"
    # Market open: 9:30-16:00 EST
    elif (est_hour == 9 and est_minute >= 30) or (10 <= est_hour < 16):
        return "🔔 open"
    # After-hours: 16:00-20:00 EST
    elif 16 <= est_hour < 20:
        return "🌙 after-hours"
    else:
        return "😴 closed"


# =============================================================================
# Main Logic
# =============================================================================

def generate_snapshot(brief: bool = False) -> str:
    """Generate the watchlist snapshot."""
    lines = []
    
    # Header
    now_sgt = datetime.now(timezone.utc) + timedelta(hours=8)
    market_status = get_market_status()
    
    lines.append(f"📊 **Watchlist Snapshot**")
    lines.append(f"_{now_sgt.strftime('%a %b %d, %H:%M')} SGT • {market_status}_\n")
    
    # Fetch all quotes at once
    symbols = [s["symbol"] for s in WATCHLIST]
    quotes = get_quotes(symbols)
    
    alerts = []
    
    for stock in WATCHLIST:
        symbol = stock["symbol"]
        quote = quotes.get(symbol, {})
        
        if not quote or "error" in quote:
            lines.append(f"**{symbol}**: ❌ No data")
            continue
        
        price = quote.get("price", 0)
        change = quote.get("change", 0)
        pct = quote.get("changePercentage", 0)  # FMP uses changePercentage
        
        change_str = format_change(change, pct)
        
        if brief:
            lines.append(f"**{symbol}** ${price:.2f} {change_str}")
        else:
            vol = quote.get("volume", 0)
            # FMP doesn't include avgVolume in quote, skip for now
            vol_note = ""
            if vol > 100_000_000:  # High volume alert threshold
                vol_note = f" • 📢 {vol/1_000_000:.0f}M vol"
            
            lines.append(f"**{symbol}** ${price:.2f} {change_str}{vol_note}")
        
        # Track significant moves
        if abs(pct) > 3:
            alerts.append(f"{symbol} {'+' if pct > 0 else ''}{pct:.1f}%")
    
    # Alerts summary
    if alerts and not brief:
        lines.append(f"\n⚠️ **Big moves:** {', '.join(alerts)}")
    
    # News section (only if not brief)
    if not brief:
        lines.append("\n📰 **Headlines:**")
        news_found = False
        
        for stock in WATCHLIST[:3]:  # Top 3 only to save API calls
            news = get_news(stock["symbol"], 1)
            if news:
                headline = news[0].get("title", "")
                if headline:
                    # Truncate long headlines
                    if len(headline) > 55:
                        headline = headline[:52] + "..."
                    lines.append(f"• **{stock['symbol']}**: {headline}")
                    news_found = True
        
        if not news_found:
            lines.append("• _No notable headlines_")
    
    return "\n".join(lines)


def save_snapshot(content: str):
    """Save snapshot to memory for reference."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    snapshot_file = MEMORY_DIR / "watchlist-snapshots.jsonl"
    
    entry = {
        "date": today,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "content": content
    }
    
    with open(snapshot_file, "a") as f:
        f.write(json.dumps(entry) + "\n")


def show_watchlist():
    """Show current watchlist config."""
    print("📋 **Current Watchlist:**\n")
    for i, stock in enumerate(WATCHLIST, 1):
        print(f"{i}. **{stock['symbol']}** ({stock['name']}) — {stock['notes']}")
    print("\n_Edit this file to modify watchlist._")


def main():
    brief = "--brief" in sys.argv
    edit = "--edit" in sys.argv
    
    if edit:
        show_watchlist()
        return
    
    try:
        snapshot = generate_snapshot(brief=brief)
        print(snapshot)
        
        if not brief:
            save_snapshot(snapshot)
    except ValueError as e:
        print(f"❌ **Error:** {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
