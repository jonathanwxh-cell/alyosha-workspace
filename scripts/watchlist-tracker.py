#!/usr/bin/env python3
"""
Watchlist Tracker - Price alerts + Earnings calendar
Uses FMP Starter tier.

Usage:
  python3 watchlist-tracker.py check      # Check prices, alert on moves
  python3 watchlist-tracker.py earnings   # Check upcoming earnings
  python3 watchlist-tracker.py add AAPL   # Add ticker to watchlist
  python3 watchlist-tracker.py remove AAPL
  python3 watchlist-tracker.py list       # Show watchlist
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

# Default watchlist if none exists
DEFAULT_WATCHLIST = {
    "tickers": ["NVDA", "AAPL", "MSFT", "GOOGL", "META", "AMZN", "TSLA"],
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

def check_prices():
    """Check prices and alert on significant moves"""
    wl = load_watchlist()
    tickers = wl.get("tickers", [])
    if not tickers:
        print("No tickers in watchlist")
        return []
    
    quotes = get_quotes(tickers)
    if not quotes:
        return []
    
    threshold = wl.get("thresholds", {}).get("daily_move_pct", 3.0)
    last_prices = wl.get("last_prices", {})
    alerts = []
    
    for ticker in tickers:
        if ticker not in quotes:
            continue
        
        q = quotes[ticker]
        price = q.get("price", 0)
        change_pct = q.get("changePercentage", q.get("changesPercentage", 0))
        prev_close = q.get("previousClose", 0)
        
        # Check daily move
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
            "timestamp": datetime.now().isoformat()
        }
    
    wl["last_prices"] = last_prices
    save_watchlist(wl)
    
    # Log alerts
    if alerts:
        with open(ALERTS_LOG, "a") as f:
            for alert in alerts:
                alert["timestamp"] = datetime.now().isoformat()
                f.write(json.dumps(alert) + "\n")
    
    return alerts

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

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == "check":
        alerts = check_prices()
        if alerts:
            print(f"🚨 {len(alerts)} price alert(s):")
            for a in alerts:
                print(f"  {a['message']}")
        else:
            print("No significant moves")
    
    elif cmd == "earnings":
        upcoming = check_earnings()
        if upcoming:
            print("📅 Upcoming earnings (next 7 days):")
            for e in upcoming:
                days = e["days_away"]
                when = "TODAY" if days == 0 else f"in {days} days"
                eps = f"EPS est: ${e['eps_estimated']:.2f}" if e['eps_estimated'] else ""
                print(f"  {e['ticker']}: {e['date']} ({when}) {eps}")
        else:
            print("No upcoming earnings for watchlist tickers")
    
    elif cmd == "add":
        if len(sys.argv) < 3:
            print("Usage: watchlist-tracker.py add TICKER")
            return
        add_ticker(sys.argv[2])
    
    elif cmd == "remove":
        if len(sys.argv) < 3:
            print("Usage: watchlist-tracker.py remove TICKER")
            return
        remove_ticker(sys.argv[2])
    
    elif cmd == "list":
        list_watchlist()
    
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)

if __name__ == "__main__":
    main()
