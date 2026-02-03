#!/usr/bin/env python3
"""
Finnhub API Client
==================

Free financial data API - news sentiment, insider transactions, recommendations.

Setup:
    1. Get free API key at https://finnhub.io/register
    2. export FINNHUB_API_KEY=your_key_here
       OR create ~/.secure/finnhub.env with: FINNHUB_API_KEY=your_key

Usage:
    python3 finnhub-client.py quote NVDA
    python3 finnhub-client.py news NVDA
    python3 finnhub-client.py sentiment NVDA
    python3 finnhub-client.py insider NVDA
    python3 finnhub-client.py recommend NVDA
    python3 finnhub-client.py earnings NVDA
    python3 finnhub-client.py peers NVDA
    python3 finnhub-client.py watchlist NVDA,AAPL,MSFT

Free tier: 60 API calls/minute
Docs: https://finnhub.io/docs/api
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

BASE_URL = "https://finnhub.io/api/v1"
API_KEY = None


def get_api_key() -> str:
    """Load API key from environment or file"""
    key = os.environ.get('FINNHUB_API_KEY')
    if key:
        return key
    
    env_paths = [
        Path.home() / '.secure/finnhub.env',
        Path('.secure/finnhub.env'),
    ]
    
    for path in env_paths:
        if path.exists():
            with open(path) as f:
                for line in f:
                    if line.startswith('FINNHUB_API_KEY='):
                        return line.split('=', 1)[1].strip()
    
    raise ValueError(
        "FINNHUB_API_KEY not found.\n"
        "Get free key at: https://finnhub.io/register\n"
        "Then: export FINNHUB_API_KEY=your_key\n"
        "Or create: ~/.secure/finnhub.env"
    )


def init():
    global API_KEY
    API_KEY = get_api_key()


def _request(endpoint: str, params: dict = None) -> Any:
    """Make authenticated API request"""
    if API_KEY is None:
        init()
    
    params = params or {}
    params['token'] = API_KEY
    
    query = urllib.parse.urlencode(params)
    url = f"{BASE_URL}/{endpoint}?{query}"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None


# === Endpoints ===

def get_quote(symbol: str) -> Dict:
    """Real-time quote"""
    data = _request('quote', {'symbol': symbol})
    if data:
        return {
            'symbol': symbol,
            'price': data.get('c'),
            'change': data.get('d'),
            'change_pct': data.get('dp'),
            'high': data.get('h'),
            'low': data.get('l'),
            'open': data.get('o'),
            'prev_close': data.get('pc'),
            'timestamp': datetime.fromtimestamp(data.get('t', 0)).isoformat()
        }
    return {'error': 'No data', 'symbol': symbol}


def get_news(symbol: str, days: int = 7) -> List[Dict]:
    """Company news"""
    end = datetime.now()
    start = end - timedelta(days=days)
    
    data = _request('company-news', {
        'symbol': symbol,
        'from': start.strftime('%Y-%m-%d'),
        'to': end.strftime('%Y-%m-%d')
    })
    
    if data:
        return [{
            'headline': n.get('headline'),
            'summary': n.get('summary', '')[:200],
            'source': n.get('source'),
            'url': n.get('url'),
            'datetime': datetime.fromtimestamp(n.get('datetime', 0)).isoformat()
        } for n in data[:10]]
    return []


def get_sentiment(symbol: str) -> Dict:
    """News sentiment and buzz"""
    data = _request('news-sentiment', {'symbol': symbol})
    if data:
        sentiment = data.get('sentiment', {})
        buzz = data.get('buzz', {})
        return {
            'symbol': symbol,
            'sentiment': {
                'score': sentiment.get('bullishPercent', 0) - sentiment.get('bearishPercent', 0),
                'bullish': sentiment.get('bullishPercent'),
                'bearish': sentiment.get('bearishPercent')
            },
            'buzz': {
                'articles_week': buzz.get('articlesInLastWeek'),
                'weekly_avg': buzz.get('weeklyAverage'),
                'buzz_ratio': buzz.get('buzz')
            },
            'company_news_score': data.get('companyNewsScore')
        }
    return {'error': 'No sentiment data', 'symbol': symbol}


def get_insider_transactions(symbol: str) -> Dict:
    """Insider transactions"""
    data = _request('stock/insider-transactions', {'symbol': symbol})
    if data and 'data' in data:
        transactions = data['data'][:20]
        buys = [t for t in transactions if t.get('transactionCode') == 'P']
        sells = [t for t in transactions if t.get('transactionCode') == 'S']
        
        return {
            'symbol': symbol,
            'total_transactions': len(transactions),
            'buys': len(buys),
            'sells': len(sells),
            'recent': [{
                'name': t.get('name'),
                'type': 'BUY' if t.get('transactionCode') == 'P' else 'SELL',
                'shares': t.get('share'),
                'value': t.get('value'),
                'date': t.get('transactionDate')
            } for t in transactions[:5]]
        }
    return {'error': 'No insider data', 'symbol': symbol}


def get_insider_sentiment(symbol: str) -> Dict:
    """Insider sentiment (MSPR - Monthly Share Purchase Ratio)"""
    data = _request('stock/insider-sentiment', {
        'symbol': symbol,
        'from': (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
        'to': datetime.now().strftime('%Y-%m-%d')
    })
    if data and 'data' in data:
        recent = data['data'][-6:] if data['data'] else []
        return {
            'symbol': symbol,
            'monthly_data': [{
                'month': f"{d.get('year')}-{d.get('month'):02d}",
                'mspr': d.get('mspr'),  # -100 to 100 (sell to buy)
                'change': d.get('change')
            } for d in recent],
            'interpretation': 'Positive MSPR = net buying, Negative = net selling'
        }
    return {'error': 'No insider sentiment', 'symbol': symbol}


def get_recommendations(symbol: str) -> Dict:
    """Analyst recommendations"""
    data = _request('stock/recommendation', {'symbol': symbol})
    if data:
        recent = data[:6]  # Last 6 months
        latest = recent[0] if recent else {}
        
        return {
            'symbol': symbol,
            'latest': {
                'period': latest.get('period'),
                'strong_buy': latest.get('strongBuy'),
                'buy': latest.get('buy'),
                'hold': latest.get('hold'),
                'sell': latest.get('sell'),
                'strong_sell': latest.get('strongSell')
            },
            'trend': [{
                'period': r.get('period'),
                'buy': r.get('strongBuy', 0) + r.get('buy', 0),
                'hold': r.get('hold'),
                'sell': r.get('sell', 0) + r.get('strongSell', 0)
            } for r in recent]
        }
    return {'error': 'No recommendations', 'symbol': symbol}


def get_earnings(symbol: str) -> Dict:
    """Earnings surprises"""
    data = _request('stock/earnings', {'symbol': symbol})
    if data:
        return {
            'symbol': symbol,
            'earnings': [{
                'period': e.get('period'),
                'actual': e.get('actual'),
                'estimate': e.get('estimate'),
                'surprise': e.get('surprise'),
                'surprise_pct': e.get('surprisePercent')
            } for e in data[:8]]
        }
    return {'error': 'No earnings data', 'symbol': symbol}


def get_peers(symbol: str) -> Dict:
    """Company peers"""
    data = _request('stock/peers', {'symbol': symbol})
    if data:
        return {
            'symbol': symbol,
            'peers': data[:10]
        }
    return {'error': 'No peers data', 'symbol': symbol}


def watchlist(symbols: List[str]) -> List[Dict]:
    """Quick overview for multiple symbols"""
    results = []
    for sym in symbols:
        quote = get_quote(sym)
        sentiment = get_sentiment(sym)
        
        results.append({
            'symbol': sym,
            'price': quote.get('price'),
            'change_pct': quote.get('change_pct'),
            'sentiment_score': sentiment.get('sentiment', {}).get('score'),
            'buzz': sentiment.get('buzz', {}).get('buzz_ratio')
        })
    return results


def test_connection():
    """Test API connection"""
    try:
        init()
        data = _request('quote', {'symbol': 'AAPL'})
        if data and 'c' in data:
            print(f"✅ Finnhub API connected")
            print(f"   AAPL: ${data['c']}")
            return True
        else:
            print("❌ API returned unexpected data")
            return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


# === CLI ===

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'test':
        test_connection()
        return
    
    if len(sys.argv) < 3 and cmd != 'test':
        print(f"Usage: {sys.argv[0]} {cmd} SYMBOL")
        sys.exit(1)
    
    symbol = sys.argv[2].upper() if len(sys.argv) > 2 else ''
    
    commands = {
        'quote': lambda: get_quote(symbol),
        'news': lambda: get_news(symbol),
        'sentiment': lambda: get_sentiment(symbol),
        'insider': lambda: get_insider_transactions(symbol),
        'insider-sentiment': lambda: get_insider_sentiment(symbol),
        'recommend': lambda: get_recommendations(symbol),
        'earnings': lambda: get_earnings(symbol),
        'peers': lambda: get_peers(symbol),
        'watchlist': lambda: watchlist(symbol.split(','))
    }
    
    if cmd in commands:
        result = commands[cmd]()
        print(json.dumps(result, indent=2))
    else:
        print(f"Unknown command: {cmd}")
        print("Commands: quote, news, sentiment, insider, recommend, earnings, peers, watchlist, test")
        sys.exit(1)


if __name__ == '__main__':
    main()
