#!/usr/bin/env python3
"""
NVDA Earnings Intelligence Dashboard - Data Fetcher
Fetches price, estimates, historical earnings, and news sentiment
"""

import json
import yfinance as yf
from datetime import datetime, timedelta
import os
import sys

# Add workspace to path for imports
sys.path.insert(0, os.path.expanduser('~/.openclaw/workspace'))

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'data.json')

def fetch_nvda_data():
    """Fetch all NVDA data for dashboard"""
    print("📊 Fetching NVDA data...")
    
    nvda = yf.Ticker("NVDA")
    
    # Current price and info
    info = nvda.info
    
    # Historical data (6 months)
    hist = nvda.history(period="6mo")
    
    # Get earnings dates
    try:
        earnings_dates = nvda.earnings_dates
        upcoming_earnings = None
        if earnings_dates is not None and len(earnings_dates) > 0:
            future_dates = earnings_dates[earnings_dates.index > datetime.now()]
            if len(future_dates) > 0:
                upcoming_earnings = str(future_dates.index[0].date())
    except:
        upcoming_earnings = "2026-02-25"  # Known date
    
    # Historical earnings (for reaction analysis)
    try:
        earnings_history = nvda.earnings_history
        if earnings_history is not None:
            earnings_hist_data = earnings_history.to_dict('records')[-8:]  # Last 8 quarters
        else:
            earnings_hist_data = []
    except:
        earnings_hist_data = []
    
    # Analyst recommendations
    try:
        recommendations = nvda.recommendations
        if recommendations is not None and len(recommendations) > 0:
            recent_recs = recommendations.tail(10).to_dict('records')
        else:
            recent_recs = []
    except:
        recent_recs = []
    
    # Build price history for chart
    price_history = []
    for date, row in hist.iterrows():
        price_history.append({
            'date': str(date.date()),
            'close': round(row['Close'], 2),
            'volume': int(row['Volume'])
        })
    
    # Compile dashboard data
    data = {
        'generated_at': datetime.now().isoformat(),
        'ticker': 'NVDA',
        'company': info.get('longName', 'NVIDIA Corporation'),
        
        # Current snapshot
        'current': {
            'price': info.get('currentPrice') or info.get('regularMarketPrice'),
            'change_pct': info.get('regularMarketChangePercent'),
            'market_cap': info.get('marketCap'),
            'pe_ratio': info.get('trailingPE'),
            'forward_pe': info.get('forwardPE'),
            'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
            'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
        },
        
        # Earnings
        'earnings': {
            'next_date': upcoming_earnings,
            'eps_estimate': info.get('forwardEps'),
            'history': earnings_hist_data,
        },
        
        # Price history
        'price_history': price_history,
        
        # Analyst sentiment
        'analysts': {
            'target_mean': info.get('targetMeanPrice'),
            'target_high': info.get('targetHighPrice'),
            'target_low': info.get('targetLowPrice'),
            'recommendation': info.get('recommendationKey'),
            'num_analysts': info.get('numberOfAnalystOpinions'),
            'recent_recommendations': recent_recs,
        },
        
        # Key metrics
        'metrics': {
            'revenue_growth': info.get('revenueGrowth'),
            'earnings_growth': info.get('earningsGrowth'),
            'profit_margin': info.get('profitMargins'),
            'roe': info.get('returnOnEquity'),
        },
        
        # Thesis tracking
        'thesis': {
            'bull': [
                'Rubin platform in production (10x cost reduction)',
                'Physical AI expansion (Cosmos, Alpamayo, GR00T)',
                'Data center demand remains strong',
                'Jevons Paradox: efficiency → more demand',
            ],
            'bear': [
                'China export restrictions impact',
                'Customer concentration risk',
                'Valuation stretched at current PE',
                'Competition from AMD, custom silicon',
            ],
            'signals_to_watch': [
                'Data center revenue growth rate',
                'China revenue guidance',
                'Gross margin trajectory',
                'Hyperscaler capex commentary',
            ]
        }
    }
    
    # Save to JSON
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"✅ Data saved to {OUTPUT_FILE}")
    return data

if __name__ == '__main__':
    data = fetch_nvda_data()
    print(f"Current price: ${data['current']['price']}")
    print(f"Next earnings: {data['earnings']['next_date']}")
