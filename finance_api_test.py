#!/usr/bin/env python3
"""
Finance API Test - Alpha Vantage vs Yahoo Finance
Demonstrates both APIs for market data monitoring
"""

import yfinance as yf
import requests
import json
from datetime import datetime

# Alpha Vantage free demo key (limited, get your own at alphavantage.co)
ALPHA_VANTAGE_KEY = "demo"  # Replace with real key for production

def test_yahoo_finance():
    """Test Yahoo Finance via yfinance library (free, unofficial)"""
    print("\n" + "="*60)
    print("📊 YAHOO FINANCE TEST (yfinance library)")
    print("="*60)
    
    # Test multiple markets
    tickers = {
        "SPY": "S&P 500 ETF (US)",
        "GC=F": "Gold Futures",
        "SI=F": "Silver Futures",
        "BTC-USD": "Bitcoin",
        "^STI": "Singapore STI",
        "D05.SI": "DBS Group (SGX)",
        "9988.HK": "Alibaba (HKEX)",
    }
    
    print("\n🔍 Fetching current prices...\n")
    
    results = []
    for symbol, name in tickers.items():
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info
            price = info.get('lastPrice') or info.get('regularMarketPrice', 'N/A')
            change = info.get('regularMarketChangePercent', 0)
            results.append({
                "symbol": symbol,
                "name": name,
                "price": f"${price:,.2f}" if isinstance(price, (int, float)) else price,
                "change": f"{change:+.2f}%" if isinstance(change, (int, float)) else "N/A"
            })
            print(f"  ✅ {symbol:10} | {name:25} | {results[-1]['price']:>12} | {results[-1]['change']:>8}")
        except Exception as e:
            print(f"  ❌ {symbol:10} | {name:25} | Error: {str(e)[:30]}")
    
    # Test historical data
    print("\n📈 Historical data test (SPY, last 5 days):")
    spy = yf.Ticker("SPY")
    hist = spy.history(period="5d")
    print(hist[['Open', 'High', 'Low', 'Close', 'Volume']].to_string())
    
    return results


def test_alpha_vantage():
    """Test Alpha Vantage API (free tier: 25 req/day)"""
    print("\n" + "="*60)
    print("📊 ALPHA VANTAGE TEST (Official API)")
    print("="*60)
    
    base_url = "https://www.alphavantage.co/query"
    
    # Test 1: Stock quote (IBM - works with demo key)
    print("\n🔍 Stock Quote (IBM)...")
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": "IBM",
        "apikey": ALPHA_VANTAGE_KEY
    }
    try:
        resp = requests.get(base_url, params=params, timeout=10)
        data = resp.json()
        if "Global Quote" in data:
            quote = data["Global Quote"]
            print(f"  ✅ IBM: ${quote.get('05. price', 'N/A')} ({quote.get('10. change percent', 'N/A')})")
        else:
            print(f"  ⚠️ Response: {data}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test 2: Forex (EUR/USD)
    print("\n🔍 Forex (EUR/USD)...")
    params = {
        "function": "CURRENCY_EXCHANGE_RATE",
        "from_currency": "EUR",
        "to_currency": "USD",
        "apikey": ALPHA_VANTAGE_KEY
    }
    try:
        resp = requests.get(base_url, params=params, timeout=10)
        data = resp.json()
        if "Realtime Currency Exchange Rate" in data:
            fx = data["Realtime Currency Exchange Rate"]
            print(f"  ✅ EUR/USD: {fx.get('5. Exchange Rate', 'N/A')}")
        else:
            print(f"  ⚠️ Response: {data}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test 3: Crypto (BTC)
    print("\n🔍 Crypto (BTC/USD)...")
    params = {
        "function": "CURRENCY_EXCHANGE_RATE",
        "from_currency": "BTC",
        "to_currency": "USD",
        "apikey": ALPHA_VANTAGE_KEY
    }
    try:
        resp = requests.get(base_url, params=params, timeout=10)
        data = resp.json()
        if "Realtime Currency Exchange Rate" in data:
            crypto = data["Realtime Currency Exchange Rate"]
            print(f"  ✅ BTC/USD: ${float(crypto.get('5. Exchange Rate', 0)):,.2f}")
        else:
            print(f"  ⚠️ Response: {data}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test 4: Technical indicator (RSI)
    print("\n🔍 Technical Indicator (RSI for IBM)...")
    params = {
        "function": "RSI",
        "symbol": "IBM",
        "interval": "daily",
        "time_period": "14",
        "series_type": "close",
        "apikey": ALPHA_VANTAGE_KEY
    }
    try:
        resp = requests.get(base_url, params=params, timeout=10)
        data = resp.json()
        if "Technical Analysis: RSI" in data:
            rsi_data = data["Technical Analysis: RSI"]
            latest_date = list(rsi_data.keys())[0]
            rsi_value = rsi_data[latest_date]["RSI"]
            print(f"  ✅ IBM RSI (14): {rsi_value} ({latest_date})")
        else:
            print(f"  ⚠️ Response: {data}")
    except Exception as e:
        print(f"  ❌ Error: {e}")


def main():
    print("\n" + "🚀 "*20)
    print("   FINANCE API TEST - Alpha Vantage vs Yahoo Finance")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("🚀 "*20)
    
    # Run tests
    yahoo_results = test_yahoo_finance()
    test_alpha_vantage()
    
    # Summary
    print("\n" + "="*60)
    print("📋 SUMMARY")
    print("="*60)
    print("""
    Yahoo Finance (yfinance):
    ✅ Broad market coverage (US, SG, HK, etc.)
    ✅ Free, no API key needed
    ✅ Historical data
    ⚠️ Unofficial, may break
    ⚠️ No built-in indicators
    
    Alpha Vantage:
    ✅ Official, stable API
    ✅ 50+ technical indicators
    ✅ Forex, crypto, stocks
    ⚠️ Free tier limited (25 req/day)
    ⚠️ Limited Asia coverage
    
    💡 Recommendation: Use BOTH
    - Yahoo for SGX, HKEX, broad coverage
    - Alpha Vantage for US + technical indicators
    """)


if __name__ == "__main__":
    main()
