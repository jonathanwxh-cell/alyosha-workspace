#!/usr/bin/env python3
"""
Earnings Calendar Tracker
=========================

Track upcoming earnings for watchlist stocks.
Alert before earnings, show expectations vs history.

Usage:
    python3 earnings-tracker.py              # Full earnings calendar
    python3 earnings-tracker.py --upcoming   # Next 30 days only
    python3 earnings-tracker.py --alerts     # Stocks with earnings this week
    python3 earnings-tracker.py NVDA         # Single stock detail
"""

import json
import urllib.request
import urllib.error
import sys
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Watchlist (sync with watchlist-snapshot.py)
WATCHLIST = ["NVDA", "AMD", "SMCI", "TSM", "AVGO", "GOOGL", "MSFT", "META", "AMZN"]

# Paths
MEMORY_DIR = Path.home() / '.openclaw/workspace/memory'
ENV_FILE = Path.home() / '.secure/fmp.env'
EARNINGS_CACHE = MEMORY_DIR / 'earnings-calendar.json'


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
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}"}
    except Exception as e:
        return {"error": str(e)}


def get_earnings_calendar_all(days_ahead: int = 90) -> list:
    """Get earnings calendar for date range, querying in chunks for better coverage."""
    all_results = []
    
    # Query in monthly chunks to get better coverage
    for chunk_start in range(0, days_ahead, 30):
        chunk_end = min(chunk_start + 30, days_ahead)
        start_date = (datetime.now() + timedelta(days=chunk_start)).strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=chunk_end)).strftime('%Y-%m-%d')
        
        data = fmp_request("earnings-calendar", {"from": start_date, "to": end_date})
        if isinstance(data, list):
            all_results.extend(data)
    
    # Deduplicate
    seen = set()
    unique = []
    for e in all_results:
        key = (e.get('symbol'), e.get('date'))
        if key not in seen:
            seen.add(key)
            unique.append(e)
    
    return unique


def get_earnings_history_all(days_back: int = 180) -> list:
    """Get historical earnings from past period."""
    today = datetime.now().strftime('%Y-%m-%d')
    past = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    
    data = fmp_request("earnings-calendar", {"from": past, "to": today})
    if isinstance(data, list):
        return data
    return []


def get_earnings_for_symbol(symbol: str, all_earnings: list) -> list:
    """Filter earnings list for specific symbol."""
    return [e for e in all_earnings if e.get('symbol') == symbol]


def format_earnings_date(date_str: str) -> str:
    """Format date for display."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        today = datetime.now()
        delta = (dt - today).days
        
        if delta < 0:
            return f"{date_str} (passed)"
        elif delta == 0:
            return f"📢 TODAY"
        elif delta == 1:
            return f"⚠️ TOMORROW"
        elif delta <= 7:
            return f"🔔 {dt.strftime('%a %b %d')} ({delta}d)"
        elif delta <= 30:
            return f"{dt.strftime('%b %d')} ({delta}d)"
        else:
            return f"{dt.strftime('%b %d')}"
    except:
        return date_str


def calculate_beat_rate(history: list) -> tuple:
    """Calculate historical beat rate."""
    if not history:
        return None, 0
    
    beats = 0
    total = 0
    for h in history:
        actual = h.get('eps')
        estimate = h.get('epsEstimated')
        if actual is not None and estimate is not None:
            total += 1
            if actual > estimate:
                beats += 1
    
    if total == 0:
        return None, 0
    return beats / total, total


def format_surprise(actual: float, estimate: float) -> str:
    """Format earnings surprise."""
    if actual is None or estimate is None:
        return "N/A"
    
    diff = actual - estimate
    pct = (diff / abs(estimate)) * 100 if estimate != 0 else 0
    
    if diff > 0:
        return f"✅ Beat by ${diff:.2f} (+{pct:.0f}%)"
    elif diff < 0:
        return f"❌ Miss by ${abs(diff):.2f} ({pct:.0f}%)"
    else:
        return "➖ In-line"


def get_full_calendar() -> dict:
    """Get earnings calendar for all watchlist stocks."""
    calendar = {}
    
    # Fetch all upcoming and historical in bulk (more efficient)
    all_upcoming = get_earnings_calendar_all(90)
    all_history = get_earnings_history_all(365)
    
    for symbol in WATCHLIST:
        upcoming = get_earnings_for_symbol(symbol, all_upcoming)
        history = get_earnings_for_symbol(symbol, all_history)
        
        # Sort by date
        upcoming.sort(key=lambda x: x.get('date', ''), reverse=False)
        history.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        # Find next earnings date
        next_earnings = None
        for e in upcoming:
            date_str = e.get('date')
            if date_str:
                try:
                    dt = datetime.strptime(date_str, "%Y-%m-%d")
                    if dt >= datetime.now():
                        next_earnings = e
                        break
                except:
                    pass
        
        # Calculate beat rate from history (where we have actual results)
        history_with_results = [h for h in history if h.get('epsActual') is not None]
        beat_rate, samples = calculate_beat_rate(history_with_results)
        
        calendar[symbol] = {
            'next': next_earnings,
            'history': history_with_results[:4],  # Last 4 quarters with results
            'beat_rate': beat_rate,
            'samples': samples
        }
    
    return calendar


def print_calendar(calendar: dict, upcoming_only: bool = False):
    """Print formatted earnings calendar."""
    print("=" * 60)
    print("📅 EARNINGS CALENDAR")
    print("=" * 60)
    
    # Sort by next earnings date
    sorted_stocks = []
    for symbol, data in calendar.items():
        next_e = data.get('next')
        if next_e and next_e.get('date'):
            try:
                dt = datetime.strptime(next_e['date'], "%Y-%m-%d")
                days_away = (dt - datetime.now()).days
                if upcoming_only and days_away > 30:
                    continue
                sorted_stocks.append((symbol, data, dt, days_away))
            except:
                if not upcoming_only:
                    sorted_stocks.append((symbol, data, datetime.max, 999))
        elif not upcoming_only:
            sorted_stocks.append((symbol, data, datetime.max, 999))
    
    sorted_stocks.sort(key=lambda x: x[2])
    
    for symbol, data, dt, days_away in sorted_stocks:
        next_e = data.get('next')
        beat_rate = data.get('beat_rate')
        
        print(f"\n**{symbol}**")
        
        if next_e:
            date_str = format_earnings_date(next_e.get('date', 'TBD'))
            eps_est = next_e.get('epsEstimated')
            rev_est = next_e.get('revenueEstimated')
            
            print(f"  📆 Next: {date_str}")
            if eps_est:
                print(f"  💰 EPS Est: ${eps_est:.2f}")
            if rev_est:
                print(f"  📊 Rev Est: ${rev_est/1e9:.1f}B")
        else:
            print("  📆 Next: Not scheduled")
        
        if beat_rate is not None:
            beat_pct = beat_rate * 100
            emoji = "🎯" if beat_rate >= 0.75 else "📊" if beat_rate >= 0.5 else "⚠️"
            print(f"  {emoji} Beat rate: {beat_pct:.0f}% (last {data['samples']}Q)")
        
        # Show last quarter result
        history = data.get('history', [])
        if history:
            last = history[0]
            surprise = format_surprise(last.get('eps'), last.get('epsEstimated'))
            print(f"  📋 Last Q: {surprise}")
    
    print("\n" + "=" * 60)


def print_alerts(calendar: dict):
    """Print only stocks with earnings this week."""
    print("🔔 EARNINGS ALERTS (Next 7 Days)")
    print("-" * 40)
    
    alerts = []
    for symbol, data in calendar.items():
        next_e = data.get('next')
        if next_e and next_e.get('date'):
            try:
                dt = datetime.strptime(next_e['date'], "%Y-%m-%d")
                days_away = (dt - datetime.now()).days
                if 0 <= days_away <= 7:
                    alerts.append((symbol, data, days_away))
            except:
                pass
    
    if not alerts:
        print("No watchlist earnings this week ✓")
        return
    
    alerts.sort(key=lambda x: x[2])
    
    for symbol, data, days_away in alerts:
        next_e = data['next']
        date_str = format_earnings_date(next_e.get('date'))
        eps_est = next_e.get('epsEstimated', 'N/A')
        
        if days_away == 0:
            print(f"📢 {symbol} reports TODAY! (EPS est: ${eps_est})")
        elif days_away == 1:
            print(f"⚠️ {symbol} reports TOMORROW (EPS est: ${eps_est})")
        else:
            print(f"🔔 {symbol} reports in {days_away} days (EPS est: ${eps_est})")


def print_single_stock(symbol: str):
    """Print detailed view for single stock."""
    print(f"📊 {symbol} EARNINGS DETAIL")
    print("=" * 40)
    
    all_upcoming = get_earnings_calendar_all(90)
    all_history = get_earnings_history_all(730)  # 2 years back
    
    upcoming = get_earnings_for_symbol(symbol, all_upcoming)
    history = get_earnings_for_symbol(symbol, all_history)
    
    # Sort
    upcoming.sort(key=lambda x: x.get('date', ''))
    history.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    # Next earnings
    next_e = None
    for e in upcoming:
        if e.get('date'):
            try:
                dt = datetime.strptime(e['date'], "%Y-%m-%d")
                if dt >= datetime.now():
                    next_e = e
                    break
            except:
                pass
    
    if next_e:
        print(f"\n📆 NEXT EARNINGS: {format_earnings_date(next_e.get('date'))}")
        eps_est = next_e.get('epsEstimated')
        rev_est = next_e.get('revenueEstimated')
        if eps_est:
            print(f"   EPS Estimate: ${eps_est:.2f}")
        if rev_est:
            print(f"   Revenue Est:  ${rev_est/1e9:.2f}B")
    else:
        print("\n📆 No upcoming earnings scheduled")
    
    # History (only entries with actual results)
    history_with_results = [h for h in history if h.get('epsActual') is not None]
    
    if history_with_results:
        print(f"\n📋 EARNINGS HISTORY")
        print("-" * 40)
        for h in history_with_results[:4]:
            date = h.get('date', 'N/A')
            actual = h.get('epsActual')
            estimate = h.get('epsEstimated')
            if actual is not None:
                surprise = format_surprise(actual, estimate)
                est_str = f"${estimate:.2f}" if estimate else "N/A"
                print(f"   {date}: ${actual:.2f} vs {est_str} → {surprise}")
        
        beat_rate, samples = calculate_beat_rate(history_with_results)
        if beat_rate is not None:
            print(f"\n   Beat Rate: {beat_rate*100:.0f}% (last {samples} quarters)")
    else:
        print("\n📋 No historical earnings data available")


def save_cache(calendar: dict):
    """Save calendar to cache."""
    cache = {
        'updated': datetime.now(timezone.utc).isoformat(),
        'calendar': calendar
    }
    with open(EARNINGS_CACHE, 'w') as f:
        json.dump(cache, f, indent=2, default=str)


def main():
    args = sys.argv[1:]
    
    if not args:
        calendar = get_full_calendar()
        print_calendar(calendar)
        save_cache(calendar)
    
    elif args[0] == '--upcoming':
        calendar = get_full_calendar()
        print_calendar(calendar, upcoming_only=True)
        save_cache(calendar)
    
    elif args[0] == '--alerts':
        calendar = get_full_calendar()
        print_alerts(calendar)
    
    elif args[0].upper() in WATCHLIST or len(args[0]) <= 5:
        print_single_stock(args[0].upper())
    
    else:
        print(f"Unknown option: {args[0]}")
        print("Usage: earnings-tracker.py [--upcoming|--alerts|SYMBOL]")


if __name__ == "__main__":
    main()
