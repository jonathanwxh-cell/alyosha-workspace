#!/usr/bin/env python3
"""
Alpha Vantage API Client
========================

Free financial data API with technical indicators and news sentiment.

Setup:
    Get free key: https://www.alphavantage.co/support/#api-key
    echo "ALPHAVANTAGE_API_KEY=your_key" > ~/.secure/alphavantage.env

Usage:
    python3 alphavantage-client.py quote NVDA
    python3 alphavantage-client.py daily NVDA
    python3 alphavantage-client.py sma NVDA --period 20
    python3 alphavantage-client.py rsi NVDA --period 14
    python3 alphavantage-client.py sentiment NVDA
    python3 alphavantage-client.py news NVDA

Rate limit: 25 calls/day (free), 75 calls/min (premium)
"""

import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

BASE_URL = "https://www.alphavantage.co/query"

def get_api_key() -> str:
    """Load API key from environment or .secure file."""
    key = os.environ.get('ALPHAVANTAGE_API_KEY')
    if key:
        return key
    
    env_path = Path.home() / '.secure/alphavantage.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.startswith('ALPHAVANTAGE_API_KEY='):
                    return line.split('=', 1)[1].strip()
    
    return None

def api_call(params: dict) -> dict:
    """Make API call with error handling."""
    key = get_api_key()
    if not key:
        print("❌ No API key. Get one free at: https://www.alphavantage.co/support/#api-key")
        print("   Then: echo 'ALPHAVANTAGE_API_KEY=your_key' > ~/.secure/alphavantage.env")
        sys.exit(1)
    
    params['apikey'] = key
    query = '&'.join(f"{k}={v}" for k, v in params.items())
    url = f"{BASE_URL}?{query}"
    
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            if 'Error Message' in data:
                print(f"❌ API Error: {data['Error Message']}")
                return None
            if 'Note' in data:
                print(f"⚠️ Rate limit: {data['Note']}")
                return None
            return data
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def quote(symbol: str):
    """Get real-time quote."""
    data = api_call({'function': 'GLOBAL_QUOTE', 'symbol': symbol})
    if not data or 'Global Quote' not in data:
        return
    
    q = data['Global Quote']
    price = float(q.get('05. price', 0))
    change = float(q.get('09. change', 0))
    pct = float(q.get('10. change percent', '0%').replace('%', ''))
    vol = int(q.get('06. volume', 0))
    
    emoji = '🟢' if change >= 0 else '🔴'
    print(f"{emoji} {symbol}: ${price:.2f} ({change:+.2f}, {pct:+.2f}%)")
    print(f"   Volume: {vol:,}")

def daily(symbol: str, days: int = 10):
    """Get daily price history."""
    data = api_call({'function': 'TIME_SERIES_DAILY', 'symbol': symbol, 'outputsize': 'compact'})
    if not data or 'Time Series (Daily)' not in data:
        return
    
    ts = data['Time Series (Daily)']
    print(f"📈 {symbol} Daily Prices (last {days} days)")
    print("-" * 50)
    
    for i, (date, vals) in enumerate(list(ts.items())[:days]):
        close = float(vals['4. close'])
        vol = int(vals['5. volume'])
        print(f"{date}: ${close:.2f} | Vol: {vol:,}")

def sma(symbol: str, period: int = 20):
    """Get Simple Moving Average."""
    data = api_call({
        'function': 'SMA',
        'symbol': symbol,
        'interval': 'daily',
        'time_period': period,
        'series_type': 'close'
    })
    if not data or 'Technical Analysis: SMA' not in data:
        return
    
    ta = data['Technical Analysis: SMA']
    print(f"📊 {symbol} SMA({period})")
    print("-" * 40)
    
    for i, (date, vals) in enumerate(list(ta.items())[:5]):
        sma_val = float(vals['SMA'])
        print(f"{date}: {sma_val:.2f}")

def rsi(symbol: str, period: int = 14):
    """Get Relative Strength Index."""
    data = api_call({
        'function': 'RSI',
        'symbol': symbol,
        'interval': 'daily',
        'time_period': period,
        'series_type': 'close'
    })
    if not data or 'Technical Analysis: RSI' not in data:
        return
    
    ta = data['Technical Analysis: RSI']
    print(f"📊 {symbol} RSI({period})")
    print("-" * 40)
    
    for i, (date, vals) in enumerate(list(ta.items())[:5]):
        rsi_val = float(vals['RSI'])
        status = '🔴 OVERBOUGHT' if rsi_val > 70 else '🟢 OVERSOLD' if rsi_val < 30 else '⚪ NEUTRAL'
        print(f"{date}: {rsi_val:.1f} {status}")

def sentiment(symbol: str):
    """Get news sentiment analysis."""
    data = api_call({
        'function': 'NEWS_SENTIMENT',
        'tickers': symbol,
        'limit': 10
    })
    if not data or 'feed' not in data:
        return
    
    print(f"📰 {symbol} News Sentiment")
    print("=" * 60)
    
    for article in data['feed'][:5]:
        title = article.get('title', '')[:60]
        source = article.get('source', 'Unknown')
        
        # Find sentiment for our symbol
        sentiment_score = 0
        for ticker in article.get('ticker_sentiment', []):
            if ticker.get('ticker') == symbol:
                sentiment_score = float(ticker.get('ticker_sentiment_score', 0))
                break
        
        emoji = '🟢' if sentiment_score > 0.1 else '🔴' if sentiment_score < -0.1 else '⚪'
        print(f"{emoji} [{source}] {title}")
        print(f"   Sentiment: {sentiment_score:+.3f}")
        print()

def news(symbol: str):
    """Get latest news."""
    data = api_call({
        'function': 'NEWS_SENTIMENT',
        'tickers': symbol,
        'limit': 10
    })
    if not data or 'feed' not in data:
        return
    
    print(f"📰 {symbol} Latest News")
    print("=" * 60)
    
    for article in data['feed'][:7]:
        title = article.get('title', '')
        source = article.get('source', 'Unknown')
        url = article.get('url', '')
        time = article.get('time_published', '')[:10]
        
        print(f"[{time}] {source}")
        print(f"  {title}")
        print()

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'quote' and len(sys.argv) >= 3:
        quote(sys.argv[2].upper())
    
    elif cmd == 'daily' and len(sys.argv) >= 3:
        days = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[3] == '--days' else 10
        daily(sys.argv[2].upper(), days)
    
    elif cmd == 'sma' and len(sys.argv) >= 3:
        period = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[3] == '--period' else 20
        sma(sys.argv[2].upper(), period)
    
    elif cmd == 'rsi' and len(sys.argv) >= 3:
        period = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[3] == '--period' else 14
        rsi(sys.argv[2].upper(), period)
    
    elif cmd == 'sentiment' and len(sys.argv) >= 3:
        sentiment(sys.argv[2].upper())
    
    elif cmd == 'news' and len(sys.argv) >= 3:
        news(sys.argv[2].upper())
    
    elif cmd == 'test':
        key = get_api_key()
        if key:
            print(f"✅ API key configured: {key[:8]}...")
            print("Testing with AAPL quote...")
            quote('AAPL')
        else:
            print("❌ No API key found")
    
    else:
        print(__doc__)

if __name__ == '__main__':
    main()
