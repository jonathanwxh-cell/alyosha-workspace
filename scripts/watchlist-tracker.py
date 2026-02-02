#!/usr/bin/env python3
"""
Watchlist Tracker - Price alerts + Earnings calendar
Uses FMP API (stable endpoints).

Usage:
  python3 watchlist-tracker.py check           # Check prices, show summary + alerts
  python3 watchlist-tracker.py check --quiet   # Only output if alerts (for cron)
  python3 watchlist-tracker.py check --json    # JSON output for piping
  python3 watchlist-tracker.py earnings        # Check upcoming earnings
  python3 watchlist-tracker.py add AAPL        # Add ticker to watchlist
  python3 watchlist-tracker.py remove AAPL
  python3 watchlist-tracker.py list            # Show watchlist + current prices
  python3 watchlist-tracker.py threshold 5.0   # Set daily alert threshold %
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Paths
WORKSPACE = Path.home() / ".openclaw" / "workspace"
WATCHLIST_FILE = WORKSPACE / "memory" / "watchlist.json"
ALERTS_LOG = WORKSPACE / "memory" / "price-alerts.jsonl"

# FMP API
def get_api_key():
    # Check multiple locations
    locations = [
        Path.home() / ".secure" / "fmp.env",
        Path.home() / ".secure" / "fmp.env",
    ]
    for env_file in locations:
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("FMP_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"\'')
    return os.environ.get("FMP_API_KEY")

API_KEY = get_api_key()
BASE_URL = "https://financialmodelingprep.com/stable"

# Default watchlist if none exists (semiconductor-focused for Jon)
DEFAULT_WATCHLIST = {
    "tickers": [
        "NVDA", "AMD", "AVGO", "TSM", "SMCI",  # Core semis
        "AAPL", "MSFT", "GOOGL", "META", "AMZN"  # Mag 7
    ],
    "thresholds": {
        "daily_move_pct": 3.0,
        "weekly_move_pct": 10.0
    },
    "last_prices": {},
    "updated": None
}

def load_watchlist():
    if WATCHLIST_FILE.exists():
        return json.loads(WATCHLIST_FILE.read_text())
    return DEFAULT_WATCHLIST.copy()

def save_watchlist(data):
    data["updated"] = datetime.now().isoformat()
    WATCHLIST_FILE.parent.mkdir(parents=True, exist_ok=True)
    WATCHLIST_FILE.write_text(json.dumps(data, indent=2))

def get_quotes(tickers):
    """Fetch quotes (individual requests for Starter tier compatibility)"""
    if not API_KEY:
        print("ERROR: FMP_API_KEY not found")
        return {}
    
    results = {}
    for ticker in tickers:
        url = f"{BASE_URL}/quote?symbol={ticker}&apikey={API_KEY}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, list) and len(data) > 0:
                results[ticker] = data[0]
            elif isinstance(data, dict) and "symbol" in data:
                results[ticker] = data
        except Exception as e:
            print(f"ERROR fetching {ticker}: {e}")
    
    return results

def get_earnings_calendar(from_date, to_date):
    """Get earnings calendar"""
    if not API_KEY:
        return []
    
    # Try stable endpoint first, fall back to v3
    urls = [
        f"{BASE_URL}/earning-calendar?from={from_date}&to={to_date}&apikey={API_KEY}",
        f"https://financialmodelingprep.com/api/v3/earning_calendar?from={from_date}&to={to_date}&apikey={API_KEY}",
    ]
    
    for url in urls:
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            continue
    
    print("ERROR: Could not fetch earnings calendar")
    return []

def check_prices(quiet=False, as_json=False):
    """Check prices and alert on significant moves.
    
    Args:
        quiet: Only return alerts (for cron jobs)
        as_json: Return JSON output
    
    Returns:
        dict with 'alerts', 'summary', and 'quotes'
    """
    wl = load_watchlist()
    tickers = wl.get("tickers", [])
    if not tickers:
        return {"error": "No tickers in watchlist", "alerts": [], "summary": None}
    
    quotes = get_quotes(tickers)
    if not quotes:
        return {"error": "Failed to fetch quotes", "alerts": [], "summary": None}
    
    threshold = wl.get("thresholds", {}).get("daily_move_pct", 3.0)
    last_prices = wl.get("last_prices", {})
    alerts = []
    summary = {"gainers": [], "losers": [], "unchanged": []}
    
    for ticker in tickers:
        if ticker not in quotes:
            continue
        
        q = quotes[ticker]
        price = q.get("price", 0)
        change_pct = q.get("changePercentage", q.get("changesPercentage", 0))
        
        # Categorize
        entry = {"ticker": ticker, "price": price, "change_pct": change_pct}
        if change_pct > 0.5:
            summary["gainers"].append(entry)
        elif change_pct < -0.5:
            summary["losers"].append(entry)
        else:
            summary["unchanged"].append(entry)
        
        # Check for alert threshold
        if abs(change_pct) >= threshold:
            direction = "📈" if change_pct > 0 else "📉"
            alerts.append({
                "ticker": ticker,
                "type": "daily_move",
                "price": price,
                "change_pct": change_pct,
                "direction": direction,
                "message": f"{direction} **{ticker}** moved {change_pct:+.1f}% → ${price:.2f}"
            })
        
        # Update last price
        last_prices[ticker] = {
            "price": price,
            "change_pct": change_pct,
            "timestamp": datetime.now().isoformat()
        }
    
    # Sort by change
    summary["gainers"].sort(key=lambda x: -x["change_pct"])
    summary["losers"].sort(key=lambda x: x["change_pct"])
    
    wl["last_prices"] = last_prices
    save_watchlist(wl)
    
    # Log alerts
    if alerts:
        ALERTS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(ALERTS_LOG, "a") as f:
            for alert in alerts:
                alert["timestamp"] = datetime.now().isoformat()
                f.write(json.dumps(alert) + "\n")
    
    return {
        "alerts": alerts,
        "summary": summary,
        "quotes": quotes,
        "threshold": threshold
    }

def format_check_output(result, quiet=False):
    """Format check results for display."""
    if "error" in result:
        return result["error"]
    
    alerts = result.get("alerts", [])
    summary = result.get("summary", {})
    threshold = result.get("threshold", 3.0)
    
    # Quiet mode: only output if alerts
    if quiet:
        if not alerts:
            return None
        return "\n".join([f"🚨 {a['message']}" for a in alerts])
    
    # Full output
    lines = [f"📊 **Watchlist Check** (alert threshold: ±{threshold}%)\n"]
    
    # Gainers
    if summary.get("gainers"):
        lines.append("🟢 **Up:**")
        for g in summary["gainers"][:5]:
            lines.append(f"   {g['ticker']}: ${g['price']:.2f} ({g['change_pct']:+.1f}%)")
    
    # Losers  
    if summary.get("losers"):
        lines.append("🔴 **Down:**")
        for l in summary["losers"][:5]:
            lines.append(f"   {l['ticker']}: ${l['price']:.2f} ({l['change_pct']:+.1f}%)")
    
    # Unchanged
    if summary.get("unchanged"):
        unchanged_tickers = [u["ticker"] for u in summary["unchanged"]]
        lines.append(f"⚪ **Flat:** {', '.join(unchanged_tickers)}")
    
    # Alerts
    if alerts:
        lines.append(f"\n🚨 **Alerts ({len(alerts)}):**")
        for a in alerts:
            lines.append(f"   {a['message']}")
    
    return "\n".join(lines)

def check_earnings():
    """Check upcoming earnings for watchlist tickers"""
    wl = load_watchlist()
    tickers = set(wl.get("tickers", []))
    
    today = datetime.now().date()
    week_out = today + timedelta(days=7)
    
    calendar = get_earnings_calendar(
        today.strftime("%Y-%m-%d"),
        week_out.strftime("%Y-%m-%d")
    )
    
    upcoming = []
    for item in calendar:
        symbol = item.get("symbol", "")
        if symbol in tickers:
            date = item.get("date", "")
            eps_est = item.get("epsEstimated")
            rev_est = item.get("revenueEstimated")
            
            days_away = (datetime.strptime(date, "%Y-%m-%d").date() - today).days
            
            upcoming.append({
                "ticker": symbol,
                "date": date,
                "days_away": days_away,
                "eps_estimated": eps_est,
                "revenue_estimated": rev_est
            })
    
    # Sort by date
    upcoming.sort(key=lambda x: x["date"])
    return upcoming

def add_ticker(ticker):
    wl = load_watchlist()
    ticker = ticker.upper()
    if ticker not in wl["tickers"]:
        wl["tickers"].append(ticker)
        save_watchlist(wl)
        print(f"Added {ticker} to watchlist")
    else:
        print(f"{ticker} already in watchlist")

def remove_ticker(ticker):
    wl = load_watchlist()
    ticker = ticker.upper()
    if ticker in wl["tickers"]:
        wl["tickers"].remove(ticker)
        save_watchlist(wl)
        print(f"Removed {ticker} from watchlist")
    else:
        print(f"{ticker} not in watchlist")

def list_watchlist():
    wl = load_watchlist()
    print(f"Watchlist ({len(wl['tickers'])} tickers):")
    print(f"  Thresholds: {wl.get('thresholds', {})}")
    print(f"  Tickers: {', '.join(wl['tickers'])}")
    
    # Also show current prices
    quotes = get_quotes(wl["tickers"])
    if quotes:
        print("\nCurrent prices:")
        for ticker in wl["tickers"]:
            if ticker in quotes:
                q = quotes[ticker]
                price = q.get('price', 0)
                change = q.get('changePercentage', 0)
                print(f"  {ticker}: ${price:.2f} ({change:+.1f}%)")

def set_threshold(value):
    """Set alert threshold percentage."""
    try:
        threshold = float(value)
        if threshold <= 0:
            print("Threshold must be positive")
            return
        
        wl = load_watchlist()
        wl["thresholds"]["daily_move_pct"] = threshold
        save_watchlist(wl)
        print(f"✅ Alert threshold set to ±{threshold}%")
    except ValueError:
        print("Invalid threshold value")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1].lower()
    args = sys.argv[2:]
    
    if cmd == "check":
        quiet = "--quiet" in args or "-q" in args
        as_json = "--json" in args
        
        result = check_prices(quiet=quiet, as_json=as_json)
        
        if as_json:
            print(json.dumps(result, indent=2))
        else:
            output = format_check_output(result, quiet=quiet)
            if output:
                print(output)
    
    elif cmd == "earnings":
        upcoming = check_earnings()
        if upcoming:
            print("📅 **Upcoming Earnings** (next 7 days)\n")
            for e in upcoming:
                days = e["days_away"]
                when = "⚡ TODAY" if days == 0 else f"in {days}d"
                eps = f" | EPS est: ${e['eps_estimated']:.2f}" if e['eps_estimated'] else ""
                print(f"  **{e['ticker']}**: {e['date']} ({when}){eps}")
        else:
            print("No upcoming earnings for watchlist tickers")
    
    elif cmd == "add":
        if not args:
            print("Usage: watchlist-tracker.py add TICKER [TICKER2 ...]")
            return
        for ticker in args:
            add_ticker(ticker)
    
    elif cmd == "remove":
        if not args:
            print("Usage: watchlist-tracker.py remove TICKER")
            return
        remove_ticker(args[0])
    
    elif cmd == "list":
        list_watchlist()
    
    elif cmd == "threshold":
        if not args:
            wl = load_watchlist()
            print(f"Current threshold: ±{wl.get('thresholds', {}).get('daily_move_pct', 3.0)}%")
            return
        set_threshold(args[0])
    
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)

if __name__ == "__main__":
    main()
