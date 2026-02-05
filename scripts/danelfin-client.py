#!/usr/bin/env python3
"""
Danelfin API Client
===================

AI-powered stock scoring - integrates with trading goal for better screening.

Setup:
    1. Subscribe at https://danelfin.com/pricing/api
    2. export DANELFIN_API_KEY=your_key_here
       OR create ~/.secure/danelfin.env with: DANELFIN_API_KEY=your_key

Usage:
    python3 danelfin-client.py score NVDA              # Get current AI scores
    python3 danelfin-client.py history NVDA 30         # 30-day score history
    python3 danelfin-client.py top                     # Today's top 100 stocks
    python3 danelfin-client.py top10                   # Top 10 by AI Score
    python3 danelfin-client.py screen 8                # Stocks with AI Score >= 8
    python3 danelfin-client.py sector technology       # Sector scores
    python3 danelfin-client.py watchlist NVDA,RTX,UNH  # Score multiple tickers

Scores (1-10, higher = better):
    - AI Score: Overall AI-powered ranking
    - Technical: Technical analysis rating
    - Fundamental: Fundamental analysis rating
    - Sentiment: Market sentiment analysis
    - Low Risk: Risk assessment (higher = lower risk)

API Tiers:
    - Basic: 1,000 calls/month, 120/min
    - Expert: 10,000 calls/month, 240/min
    - Elite: 100,000 calls/month, 1,200/min

Docs: https://danelfin.com/docs/api
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

BASE_URL = "https://apirest.danelfin.com"
API_KEY = None


def get_api_key() -> str:
    """Load API key from environment or file"""
    key = os.environ.get('DANELFIN_API_KEY')
    if key:
        return key
    
    env_paths = [
        Path.home() / '.secure/danelfin.env',
        Path('.secure/danelfin.env'),
    ]
    
    for path in env_paths:
        if path.exists():
            content = path.read_text().strip()
            for line in content.split('\n'):
                if line.startswith('DANELFIN_API_KEY='):
                    return line.split('=', 1)[1].strip()
    
    return None


def api_request(endpoint: str, params: Dict = None) -> Dict:
    """Make API request to Danelfin"""
    global API_KEY
    if not API_KEY:
        API_KEY = get_api_key()
        if not API_KEY:
            print("ERROR: No API key found. Set DANELFIN_API_KEY or create ~/.secure/danelfin.env")
            sys.exit(1)
    
    url = f"{BASE_URL}/{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    
    req = urllib.request.Request(url)
    req.add_header('x-api-key', API_KEY)
    req.add_header('Accept', 'application/json')
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print("ERROR: Invalid API key or insufficient permissions")
        elif e.code == 400:
            print(f"ERROR: Bad request - {e.read().decode()}")
        else:
            print(f"ERROR: HTTP {e.code}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


def format_scores(scores: Dict) -> str:
    """Format scores for display"""
    ai = scores.get('aiscore', 'N/A')
    tech = scores.get('technical', 'N/A')
    fund = scores.get('fundamental', 'N/A')
    sent = scores.get('sentiment', 'N/A')
    risk = scores.get('low_risk', 'N/A')
    
    # Color coding (terminal)
    def color(val):
        if val == 'N/A':
            return val
        v = int(val) if isinstance(val, str) else val
        if v >= 8:
            return f"\033[92m{v}\033[0m"  # Green
        elif v >= 5:
            return f"\033[93m{v}\033[0m"  # Yellow
        else:
            return f"\033[91m{v}\033[0m"  # Red
    
    return f"AI:{color(ai)} Tech:{color(tech)} Fund:{color(fund)} Sent:{color(sent)} Risk:{color(risk)}"


def cmd_score(ticker: str):
    """Get current AI scores for a ticker"""
    today = datetime.now().strftime('%Y-%m-%d')
    # Try today, then previous trading days
    for days_back in range(0, 5):
        date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        data = api_request('ranking', {'ticker': ticker.upper(), 'date': date})
        if data:
            break
    
    if not data:
        print(f"No data found for {ticker}")
        return
    
    print(f"\n📊 {ticker.upper()} - Danelfin AI Scores")
    print("=" * 40)
    
    # Data format: {"date": {"aiscore": X, ...}}
    for date, scores in sorted(data.items(), reverse=True)[:1]:
        print(f"Date: {date}")
        print(format_scores(scores))
        
        ai = int(scores.get('aiscore', 0))
        if ai >= 8:
            print("\n✅ STRONG BUY signal (AI Score 8-10)")
        elif ai >= 6:
            print("\n📈 BUY signal (AI Score 6-7)")
        elif ai <= 3:
            print("\n⚠️ SELL signal (AI Score 1-3)")


def cmd_history(ticker: str, days: int = 30):
    """Get score history for a ticker"""
    data = api_request('ranking', {'ticker': ticker.upper()})
    
    if not data:
        print(f"No data found for {ticker}")
        return
    
    print(f"\n📈 {ticker.upper()} - {days}-Day Score History")
    print("=" * 50)
    
    # Sort by date descending, take last N days
    sorted_dates = sorted(data.items(), reverse=True)[:days]
    
    for date, scores in sorted_dates:
        print(f"{date}: {format_scores(scores)}")


def cmd_top(date: str = None):
    """Get top 100 stocks by AI Score"""
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    
    data = api_request('ranking', {'date': date, 'aiscore_min': 1})
    
    if not data:
        print(f"No data for {date}")
        return
    
    print(f"\n🏆 Top Stocks by AI Score - {date}")
    print("=" * 50)
    
    # Data format: {"date": {"TICKER": {...}, ...}}
    if date in data:
        stocks = data[date]
    else:
        stocks = data
    
    # Sort by AI score
    sorted_stocks = sorted(
        stocks.items(),
        key=lambda x: int(x[1].get('aiscore', 0)),
        reverse=True
    )
    
    for ticker, scores in sorted_stocks[:20]:
        print(f"{ticker:6} {format_scores(scores)}")


def cmd_top10():
    """Get top 10 stocks with AI Score = 10"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    for days_back in range(0, 5):
        date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        data = api_request('ranking', {'date': date, 'aiscore': 10})
        if data:
            break
    
    if not data:
        print("No stocks with AI Score 10 found")
        return
    
    print(f"\n⭐ AI Score 10 Stocks (Perfect Score)")
    print("=" * 50)
    
    stocks = data.get(date, data)
    for ticker, scores in list(stocks.items())[:10]:
        print(f"{ticker:6} {format_scores(scores)}")


def cmd_screen(min_score: int = 8):
    """Screen for stocks with minimum AI Score"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    for days_back in range(0, 5):
        date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        data = api_request('ranking', {'date': date, 'aiscore_min': min_score})
        if data:
            break
    
    if not data:
        print(f"No stocks with AI Score >= {min_score}")
        return
    
    print(f"\n🔍 Stocks with AI Score >= {min_score}")
    print("=" * 50)
    
    stocks = data.get(date, data)
    sorted_stocks = sorted(
        stocks.items(),
        key=lambda x: int(x[1].get('aiscore', 0)),
        reverse=True
    )
    
    for ticker, scores in sorted_stocks[:30]:
        print(f"{ticker:6} {format_scores(scores)}")


def cmd_sector(sector_slug: str):
    """Get sector scores history"""
    data = api_request(f'sectors/{sector_slug}')
    
    if not data:
        print(f"No data for sector: {sector_slug}")
        return
    
    print(f"\n📊 Sector: {sector_slug}")
    print("=" * 50)
    
    scores = data.get('scores', [])[-10:]  # Last 10 data points
    for entry in reversed(scores):
        date = entry.get('date', 'N/A')
        print(f"{date}: AI:{entry.get('aiscore')} Tech:{entry.get('technical')} Fund:{entry.get('fundamental')}")


def cmd_sectors():
    """List all available sectors"""
    data = api_request('sectors')
    
    print("\n📋 Available Sectors")
    print("=" * 30)
    for item in data:
        print(f"  - {item.get('sector')}")


def cmd_watchlist(tickers: str):
    """Get scores for multiple tickers"""
    ticker_list = [t.strip().upper() for t in tickers.split(',')]
    
    print(f"\n📋 Watchlist Scores")
    print("=" * 50)
    
    for ticker in ticker_list:
        for days_back in range(0, 5):
            date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            data = api_request('ranking', {'ticker': ticker, 'date': date})
            if data:
                break
        
        if data:
            for d, scores in list(data.items())[:1]:
                ai = int(scores.get('aiscore', 0))
                signal = "⭐" if ai >= 8 else "📈" if ai >= 6 else "⚠️" if ai <= 3 else "  "
                print(f"{signal} {ticker:6} {format_scores(scores)}")
        else:
            print(f"   {ticker:6} No data")


def cmd_trading_screen():
    """Screen for trading goal - high AI + low risk"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    for days_back in range(0, 5):
        date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        data = api_request('ranking', {
            'date': date,
            'aiscore_min': 7,
            'low_risk_min': 6
        })
        if data:
            break
    
    if not data:
        print("No qualifying stocks found")
        return
    
    print(f"\n🎯 Trading Goal Screen: AI >= 7, Risk >= 6")
    print("=" * 50)
    
    stocks = data.get(date, data)
    # Sort by AI score, then risk
    sorted_stocks = sorted(
        stocks.items(),
        key=lambda x: (int(x[1].get('aiscore', 0)), int(x[1].get('low_risk', 0))),
        reverse=True
    )
    
    for ticker, scores in sorted_stocks[:20]:
        print(f"{ticker:6} {format_scores(scores)}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'score' and len(sys.argv) >= 3:
        cmd_score(sys.argv[2])
    elif cmd == 'history' and len(sys.argv) >= 3:
        days = int(sys.argv[3]) if len(sys.argv) >= 4 else 30
        cmd_history(sys.argv[2], days)
    elif cmd == 'top':
        date = sys.argv[2] if len(sys.argv) >= 3 else None
        cmd_top(date)
    elif cmd == 'top10':
        cmd_top10()
    elif cmd == 'screen':
        min_score = int(sys.argv[2]) if len(sys.argv) >= 3 else 8
        cmd_screen(min_score)
    elif cmd == 'sector' and len(sys.argv) >= 3:
        cmd_sector(sys.argv[2])
    elif cmd == 'sectors':
        cmd_sectors()
    elif cmd == 'watchlist' and len(sys.argv) >= 3:
        cmd_watchlist(sys.argv[2])
    elif cmd == 'trading':
        cmd_trading_screen()
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
