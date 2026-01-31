#!/usr/bin/env python3
"""
🤖 AUTONOMOUS RESEARCH AGENT DEMO
Multi-step workflow showcasing agent capabilities
"""

import yfinance as yf
import requests
import json
from datetime import datetime
import os

# Config
OPENAI_KEY = "REDACTED"
ALPHA_VANTAGE_KEY = "054D8110ZPMDWOZL"
TARGET_TICKER = "NVDA"  # NVIDIA - hot topic

print("="*60)
print("🤖 AUTONOMOUS RESEARCH AGENT - INITIALIZING")
print(f"⏰ {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
print(f"🎯 Target: {TARGET_TICKER}")
print("="*60)

# STEP 1: Gather market data
print("\n📊 STEP 1: Gathering market data...")
ticker = yf.Ticker(TARGET_TICKER)
info = ticker.info

company_data = {
    "name": info.get("longName"),
    "price": info.get("currentPrice"),
    "market_cap": info.get("marketCap"),
    "pe_ratio": info.get("trailingPE"),
    "forward_pe": info.get("forwardPE"),
    "revenue": info.get("totalRevenue"),
    "revenue_growth": info.get("revenueGrowth"),
    "profit_margin": info.get("profitMargins"),
    "52w_high": info.get("fiftyTwoWeekHigh"),
    "52w_low": info.get("fiftyTwoWeekLow"),
    "analyst_target": info.get("targetMeanPrice"),
    "recommendation": info.get("recommendationKey"),
}
print(f"   ✅ {company_data['name']}: ${company_data['price']}")

# STEP 2: Calculate technicals
print("\n📈 STEP 2: Calculating technical indicators...")
hist = ticker.history(period="3mo")
close = hist['Close']

# RSI
delta = close.diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
rsi = 100 - (100 / (1 + rs))

# SMAs
sma_20 = close.rolling(window=20).mean().iloc[-1]
sma_50 = close.rolling(window=50).mean().iloc[-1]

technicals = {
    "rsi": round(rsi.iloc[-1], 2),
    "sma_20": round(sma_20, 2),
    "sma_50": round(sma_50, 2),
    "price_vs_sma20": round((close.iloc[-1]/sma_20 - 1) * 100, 2),
    "price_vs_sma50": round((close.iloc[-1]/sma_50 - 1) * 100, 2),
}
print(f"   ✅ RSI: {technicals['rsi']}, SMA20: ${technicals['sma_20']}")

# STEP 3: Get news sentiment from Alpha Vantage
print("\n📰 STEP 3: Analyzing news sentiment...")
try:
    av_url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={TARGET_TICKER}&apikey={ALPHA_VANTAGE_KEY}&limit=5"
    response = requests.get(av_url, timeout=15)
    news_data = response.json()
    
    if "feed" in news_data:
        headlines = []
        sentiments = []
        for article in news_data["feed"][:5]:
            headlines.append(article.get("title", "")[:80])
            sentiments.append(article.get("overall_sentiment_score", 0))
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        print(f"   ✅ {len(headlines)} headlines analyzed, avg sentiment: {avg_sentiment:.3f}")
    else:
        headlines = ["News data unavailable"]
        avg_sentiment = 0
        print("   ⚠️ News sentiment unavailable")
except Exception as e:
    headlines = ["Error fetching news"]
    avg_sentiment = 0
    print(f"   ❌ News error: {e}")

# STEP 4: Get AI analysis from GPT
print("\n🧠 STEP 4: Running AI deep analysis...")

analysis_prompt = f"""Analyze {TARGET_TICKER} ({company_data['name']}) as a senior equity analyst. Be concise but insightful.

DATA:
- Price: ${company_data['price']}
- Market Cap: ${company_data['market_cap']:,}
- P/E: {company_data['pe_ratio']:.1f}x (Forward: {company_data['forward_pe']:.1f}x)
- Revenue Growth: {company_data['revenue_growth']*100:.1f}%
- Profit Margin: {company_data['profit_margin']*100:.1f}%
- RSI(14): {technicals['rsi']}
- vs 52W High: {((company_data['price']/company_data['52w_high'])-1)*100:.1f}%
- Analyst Target: ${company_data['analyst_target']}
- News Sentiment: {avg_sentiment:.3f} (scale -1 to +1)

Recent Headlines:
{chr(10).join(f"- {h}" for h in headlines[:3])}

Provide:
1. BULL CASE (2 sentences)
2. BEAR CASE (2 sentences)  
3. KEY RISK (1 sentence)
4. VERDICT (BUY/HOLD/SELL + 1 sentence why)
"""

try:
    gpt_response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": analysis_prompt}],
            "max_tokens": 500,
            "temperature": 0.7
        },
        timeout=30
    )
    ai_analysis = gpt_response.json()["choices"][0]["message"]["content"]
    print("   ✅ AI analysis complete")
except Exception as e:
    ai_analysis = f"AI analysis unavailable: {e}"
    print(f"   ❌ AI error: {e}")

# STEP 5: Generate image
print("\n🎨 STEP 5: Generating visual representation...")
try:
    img_response = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={
            "Authorization": f"Bearer {OPENAI_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "dall-e-3",
            "prompt": f"Abstract visualization of {company_data['name']}'s stock performance - {'bullish green ascending' if technicals['rsi'] > 50 else 'bearish red descending'} energy, circuit board patterns merging with financial charts, futuristic digital art, dramatic lighting",
            "n": 1,
            "size": "1024x1024",
            "quality": "standard"
        },
        timeout=60
    )
    img_url = img_response.json()["data"][0]["url"]
    
    # Download image
    img_data = requests.get(img_url, timeout=30)
    img_path = f"/home/ubuntu/.openclaw/workspace/{TARGET_TICKER}_analysis.png"
    with open(img_path, "wb") as f:
        f.write(img_data.content)
    print(f"   ✅ Image saved: {img_path}")
except Exception as e:
    img_path = None
    print(f"   ❌ Image error: {e}")

# STEP 6: Compile report
print("\n📝 STEP 6: Compiling final report...")

report = f"""
🤖 **AUTONOMOUS RESEARCH AGENT REPORT**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**{company_data['name']} ({TARGET_TICKER})**
Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

━━━ SNAPSHOT ━━━
💰 Price: **${company_data['price']:,.2f}**
📊 Market Cap: ${company_data['market_cap']/1e9:.1f}B
📈 Revenue Growth: {company_data['revenue_growth']*100:.1f}%
💹 P/E: {company_data['pe_ratio']:.1f}x | Fwd: {company_data['forward_pe']:.1f}x

━━━ TECHNICALS ━━━
RSI(14): **{technicals['rsi']}** {'🔴 Oversold' if technicals['rsi'] < 30 else '🟢 Overbought' if technicals['rsi'] > 70 else '⚪ Neutral'}
vs SMA20: {technicals['price_vs_sma20']:+.1f}%
vs SMA50: {technicals['price_vs_sma50']:+.1f}%
vs 52W High: {((company_data['price']/company_data['52w_high'])-1)*100:.1f}%

━━━ SENTIMENT ━━━
News Score: {avg_sentiment:.3f} {'📈' if avg_sentiment > 0 else '📉'}
Analyst Rating: **{company_data['recommendation'].upper()}**
Price Target: ${company_data['analyst_target']:.2f} ({((company_data['analyst_target']/company_data['price'])-1)*100:+.1f}%)

━━━ AI ANALYSIS ━━━
{ai_analysis}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
*5 data sources • 6 autonomous steps • 1 report*
"""

# Save report
report_path = f"/home/ubuntu/.openclaw/workspace/{TARGET_TICKER}_report.md"
with open(report_path, "w") as f:
    f.write(report)
print(f"   ✅ Report saved: {report_path}")

# Output for sending
print("\n" + "="*60)
print("✅ AGENT WORKFLOW COMPLETE")
print("="*60)
print(f"\n📄 Report path: {report_path}")
print(f"🖼️ Image path: {img_path}")
print("\n--- REPORT PREVIEW ---")
print(report)
