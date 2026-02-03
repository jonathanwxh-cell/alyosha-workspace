#!/usr/bin/env python3
"""
Benzinga API Client
===================

Python client for Benzinga financial data and news.

Setup:
    export BENZINGA_API_KEY=your_key_here
    # OR create .secure/benzinga.env with: BENZINGA_API_KEY=your_key

Usage:
    python3 benzinga-client.py news NVDA
    python3 benzinga-client.py ratings NVDA
    python3 benzinga-client.py earnings NVDA
    python3 benzinga-client.py movers
    python3 benzinga-client.py calendar --type earnings
    python3 benzinga-client.py watchlist NVDA,AAPL,MSFT

API Docs: https://docs.benzinga.com
Official Python lib: pip install benzingaorg
"""

import os
import sys
import json
import urllib.request
import urllib.error
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime, timedelta

# Base URLs for different Benzinga APIs
BASE_URL = "https://api.benzinga.com/api/v2"
NEWS_URL = "https://api.benzinga.com/api/v2/news"
CALENDAR_URL = "https://api.benzinga.com/api/v2.1/calendar"

API_KEY = None

def get_api_key() -> str:
    """Load Benzinga API key from environment or .secure/benzinga.env"""
    key = os.environ.get('BENZINGA_API_KEY')
    if key:
        return key
    
    env_paths = [
        Path.home() / '.secure/benzinga.env',
        Path('.secure/benzinga.env'),
        Path('benzinga.env'),
    ]
    
    for path in env_paths:
        if path.exists():
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('BENZINGA_API_KEY='):
                        return line.split('=', 1)[1].strip()
    
    raise ValueError(
        "BENZINGA_API_KEY not found.\n"
        "Set it via: export BENZINGA_API_KEY=your_key\n"
        "Or create: .secure/benzinga.env with BENZINGA_API_KEY=your_key"
    )

def init():
    """Initialize client with API key"""
    global API_KEY
    API_KEY = get_api_key()

def _request(url: str, params: dict = None) -> Any:
    """Make API request with authentication"""
    if API_KEY is None:
        init()
    
    # Build query string with token
    params = params or {}
    params['token'] = API_KEY
    query = '&'.join(f"{k}={v}" for k, v in params.items() if v is not None)
    full_url = f"{url}?{query}" if query else url
    
    req = urllib.request.Request(full_url)
    req.add_header('Accept', 'application/json')
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "detail": body}
    except Exception as e:
        return {"error": str(e)}

# ============================================================
# News Data Methods
# ============================================================

def get_news(
    tickers: str = None,
    topics: str = None,
    channels: str = None,
    page: int = 0,
    pagesize: int = 15,
    display_output: str = 'full',
    date_from: str = None,
    date_to: str = None
) -> Dict:
    """
    Get news articles.
    
    Args:
        tickers: Comma-separated tickers (e.g., "NVDA,AAPL")
        topics: Topics to filter (e.g., "technology,earnings")
        channels: News channels
        page: Page number for pagination
        pagesize: Results per page (max 100)
        display_output: 'full' or 'headline'
        date_from: Start date YYYY-MM-DD
        date_to: End date YYYY-MM-DD
    """
    params = {
        'page': page,
        'pageSize': pagesize,
        'displayOutput': display_output,
    }
    
    if tickers:
        params['tickers'] = tickers.upper()
    if topics:
        params['topics'] = topics
    if channels:
        params['channels'] = channels
    if date_from:
        params['dateFrom'] = date_from
    if date_to:
        params['dateTo'] = date_to
    
    return _request(NEWS_URL, params)

# ============================================================
# Financial Data Methods
# ============================================================

def get_ratings(
    tickers: str = None,
    date_from: str = None,
    date_to: str = None,
    page: int = 0,
    pagesize: int = 50,
    action: str = None
) -> Dict:
    """
    Get analyst ratings.
    
    Args:
        tickers: Comma-separated tickers
        date_from: Start date
        date_to: End date
        action: Filter by action (Upgrades, Downgrades, Maintains, etc.)
    """
    params = {
        'page': page,
        'pagesize': pagesize,
    }
    
    if tickers:
        params['parameters[tickers]'] = tickers.upper()
    if date_from:
        params['parameters[date_from]'] = date_from
    if date_to:
        params['parameters[date_to]'] = date_to
    if action:
        params['parameters[action]'] = action
    
    return _request(f"{CALENDAR_URL}/ratings", params)

def get_earnings(
    tickers: str = None,
    date_from: str = None,
    date_to: str = None,
    page: int = 0,
    pagesize: int = 50
) -> Dict:
    """
    Get earnings calendar data.
    
    Args:
        tickers: Comma-separated tickers
        date_from: Start date
        date_to: End date
    """
    params = {
        'page': page,
        'pagesize': pagesize,
    }
    
    if tickers:
        params['parameters[tickers]'] = tickers.upper()
    if date_from:
        params['parameters[date_from]'] = date_from
    if date_to:
        params['parameters[date_to]'] = date_to
    
    return _request(f"{CALENDAR_URL}/earnings", params)

def get_dividends(
    tickers: str = None,
    date_from: str = None,
    date_to: str = None,
    page: int = 0,
    pagesize: int = 50
) -> Dict:
    """Get dividend calendar data."""
    params = {
        'page': page,
        'pagesize': pagesize,
    }
    
    if tickers:
        params['parameters[tickers]'] = tickers.upper()
    if date_from:
        params['parameters[date_from]'] = date_from
    if date_to:
        params['parameters[date_to]'] = date_to
    
    return _request(f"{CALENDAR_URL}/dividends", params)

def get_guidance(
    tickers: str = None,
    date_from: str = None,
    date_to: str = None,
    page: int = 0,
    pagesize: int = 50
) -> Dict:
    """Get company guidance data."""
    params = {
        'page': page,
        'pagesize': pagesize,
    }
    
    if tickers:
        params['parameters[tickers]'] = tickers.upper()
    if date_from:
        params['parameters[date_from]'] = date_from
    if date_to:
        params['parameters[date_to]'] = date_to
    
    return _request(f"{CALENDAR_URL}/guidance", params)

def get_economics(
    country: str = "US",
    date_from: str = None,
    date_to: str = None,
    page: int = 0,
    pagesize: int = 50
) -> Dict:
    """Get economic calendar events."""
    params = {
        'page': page,
        'pagesize': pagesize,
        'parameters[country]': country,
    }
    
    if date_from:
        params['parameters[date_from]'] = date_from
    if date_to:
        params['parameters[date_to]'] = date_to
    
    return _request(f"{CALENDAR_URL}/economics", params)

def get_ipos(
    date_from: str = None,
    date_to: str = None,
    page: int = 0,
    pagesize: int = 50
) -> Dict:
    """Get IPO calendar."""
    params = {
        'page': page,
        'pagesize': pagesize,
    }
    
    if date_from:
        params['parameters[date_from]'] = date_from
    if date_to:
        params['parameters[date_to]'] = date_to
    
    return _request(f"{CALENDAR_URL}/ipos", params)

# ============================================================
# Composite Functions (for easy use)
# ============================================================

def news_summary(tickers: str, days: int = 7) -> str:
    """
    Get formatted news summary for tickers.
    
    Args:
        tickers: Comma-separated tickers
        days: Days to look back
    """
    date_from = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    result = get_news(tickers=tickers, date_from=date_from, pagesize=10)
    
    if 'error' in result:
        return f"Error: {result.get('error')}"
    
    articles = result if isinstance(result, list) else result.get('articles', result.get('data', []))
    
    if not articles:
        return f"No news found for {tickers} in last {days} days"
    
    lines = [f"📰 **{tickers} News** (last {days} days)\n"]
    
    for article in articles[:10]:
        if isinstance(article, dict):
            title = article.get('title', 'No title')
            created = article.get('created', article.get('date', ''))[:10]
            lines.append(f"• [{created}] {title[:80]}...")
    
    return '\n'.join(lines)

def ratings_summary(tickers: str, days: int = 30) -> str:
    """
    Get formatted analyst ratings summary.
    
    Args:
        tickers: Comma-separated tickers
        days: Days to look back
    """
    date_from = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    result = get_ratings(tickers=tickers, date_from=date_from)
    
    if 'error' in result:
        return f"Error: {result.get('error')}"
    
    ratings = result.get('ratings', result.get('data', []))
    
    if not ratings:
        return f"No ratings found for {tickers} in last {days} days"
    
    lines = [f"⭐ **{tickers} Analyst Ratings** (last {days} days)\n"]
    
    for r in ratings[:15]:
        if isinstance(r, dict):
            ticker = r.get('ticker', '?')
            action = r.get('action_company', r.get('action', '?'))
            firm = r.get('analyst_name', r.get('firm', '?'))
            rating = r.get('rating_current', '?')
            pt = r.get('pt_current', '')
            date = r.get('date', '')[:10]
            
            pt_str = f" PT ${pt}" if pt else ""
            lines.append(f"• [{date}] **{ticker}**: {action} → {rating}{pt_str} ({firm})")
    
    return '\n'.join(lines)

def earnings_calendar(tickers: str = None, days_ahead: int = 14) -> str:
    """
    Get upcoming earnings for tickers.
    
    Args:
        tickers: Comma-separated tickers (optional, gets all if not specified)
        days_ahead: Days to look ahead
    """
    date_from = datetime.now().strftime('%Y-%m-%d')
    date_to = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
    
    result = get_earnings(tickers=tickers, date_from=date_from, date_to=date_to)
    
    if 'error' in result:
        return f"Error: {result.get('error')}"
    
    earnings = result.get('earnings', result.get('data', []))
    
    if not earnings:
        ticker_str = tickers if tickers else "watchlist"
        return f"No upcoming earnings for {ticker_str} in next {days_ahead} days"
    
    lines = ["📅 **Upcoming Earnings**\n"]
    
    for e in earnings[:20]:
        if isinstance(e, dict):
            ticker = e.get('ticker', '?')
            name = e.get('name', '')[:20]
            date = e.get('date', '')[:10]
            time = e.get('time', '')
            eps_est = e.get('eps_est', '?')
            rev_est = e.get('revenue_est', '?')
            
            time_str = f" ({time})" if time else ""
            lines.append(f"• **{ticker}** ({name}) - {date}{time_str}")
            lines.append(f"  EPS Est: ${eps_est} | Rev Est: ${rev_est}")
    
    return '\n'.join(lines)

def watchlist_intel(tickers: str) -> str:
    """
    Comprehensive intel for a watchlist.
    
    Args:
        tickers: Comma-separated tickers
    """
    lines = [f"📊 **Watchlist Intelligence: {tickers}**\n"]
    
    # Recent news
    lines.append("**📰 Recent News:**")
    news = get_news(tickers=tickers, pagesize=5)
    articles = news if isinstance(news, list) else news.get('articles', news.get('data', []))
    if articles:
        for a in articles[:3]:
            title = a.get('title', '')[:60]
            lines.append(f"  • {title}...")
    else:
        lines.append("  • No recent news")
    
    lines.append("")
    
    # Recent ratings
    lines.append("**⭐ Recent Ratings:**")
    date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    ratings = get_ratings(tickers=tickers, date_from=date_from)
    ratings_data = ratings.get('ratings', ratings.get('data', []))
    if ratings_data:
        for r in ratings_data[:3]:
            ticker = r.get('ticker', '?')
            action = r.get('action_company', '?')
            firm = r.get('analyst_name', '?')
            lines.append(f"  • {ticker}: {action} ({firm})")
    else:
        lines.append("  • No recent ratings")
    
    lines.append("")
    
    # Upcoming earnings
    lines.append("**📅 Upcoming Earnings:**")
    date_to = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    earnings = get_earnings(tickers=tickers, date_from=datetime.now().strftime('%Y-%m-%d'), date_to=date_to)
    earnings_data = earnings.get('earnings', earnings.get('data', []))
    if earnings_data:
        for e in earnings_data[:3]:
            ticker = e.get('ticker', '?')
            date = e.get('date', '')[:10]
            lines.append(f"  • {ticker}: {date}")
    else:
        lines.append("  • No upcoming earnings in next 30 days")
    
    return '\n'.join(lines)

# ============================================================
# CLI Interface
# ============================================================

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    try:
        init()
    except ValueError as e:
        print(f"Error: {e}")
        print("\nTo use this client, you need a Benzinga API key.")
        print("Get one at: https://cloud.benzinga.com/")
        return
    
    cmd = sys.argv[1].lower()
    args = sys.argv[2:]
    
    if cmd == 'news' and args:
        print(news_summary(args[0]))
    
    elif cmd == 'ratings' and args:
        print(ratings_summary(args[0]))
    
    elif cmd == 'earnings':
        tickers = args[0] if args else None
        print(earnings_calendar(tickers))
    
    elif cmd == 'calendar' and '--type' in args:
        idx = args.index('--type')
        cal_type = args[idx + 1] if idx + 1 < len(args) else 'earnings'
        
        if cal_type == 'earnings':
            print(earnings_calendar())
        elif cal_type == 'economics':
            result = get_economics()
            print(json.dumps(result, indent=2))
        elif cal_type == 'ipos':
            result = get_ipos()
            print(json.dumps(result, indent=2))
    
    elif cmd == 'watchlist' and args:
        print(watchlist_intel(args[0]))
    
    elif cmd == 'test':
        # Test mode - just verify API key works
        result = get_news(tickers='AAPL', pagesize=1)
        if 'error' in result:
            print(f"❌ API test failed: {result.get('error')}")
        else:
            print("✅ Benzinga API key is valid!")
    
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)

if __name__ == '__main__':
    main()
