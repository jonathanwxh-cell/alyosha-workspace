#!/usr/bin/env node
/**
 * Market Intelligence Briefing Tool
 * 
 * Aggregates market data and semiconductor news into a clean briefing.
 * Built by Alyosha for Jon.
 * 
 * Usage:
 *   node market-intel.js              # Full briefing
 *   node market-intel.js --json       # JSON output
 *   node market-intel.js --quick      # Quick summary only
 */

const https = require('https');
const http = require('http');

// ─────────────────────────────────────────────────────────────
// Configuration
// ─────────────────────────────────────────────────────────────

const WATCHLIST = {
  indices: ['SPY', 'QQQ', 'DIA'],
  semiconductors: ['NVDA', 'AMD', 'TSM', 'AVGO', 'INTC', 'MU'],
  keywords: ['nvidia', 'semiconductor', 'AI chip', 'GPU', 'data center']
};

// ─────────────────────────────────────────────────────────────
// HTTP Helpers
// ─────────────────────────────────────────────────────────────

function fetch(url, options = {}) {
  return new Promise((resolve, reject) => {
    const protocol = url.startsWith('https') ? https : http;
    const req = protocol.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; MarketIntel/1.0)',
        ...options.headers
      },
      timeout: 10000
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve({ status: res.statusCode, data, headers: res.headers });
        } else {
          reject(new Error(`HTTP ${res.statusCode}: ${data.slice(0, 200)}`));
        }
      });
    });
    req.on('error', reject);
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });
  });
}

// ─────────────────────────────────────────────────────────────
// Data Sources
// ─────────────────────────────────────────────────────────────

async function getFearGreedIndex() {
  try {
    const { data } = await fetch('https://production.dataviz.cnn.io/index/fearandgreed/graphdata');
    const json = JSON.parse(data);
    const current = json.fear_and_greed;
    return {
      score: Math.round(current.score),
      rating: current.rating,
      previous: Math.round(current.previous_close),
      weekAgo: Math.round(json.fear_and_greed_historical?.one_week_ago || 0)
    };
  } catch (e) {
    return { error: e.message };
  }
}

async function getMarketStatus() {
  // Check if US markets are open (rough check)
  const now = new Date();
  const nyHour = new Date(now.toLocaleString('en-US', { timeZone: 'America/New_York' })).getHours();
  const nyDay = new Date(now.toLocaleString('en-US', { timeZone: 'America/New_York' })).getDay();
  
  const isWeekend = nyDay === 0 || nyDay === 6;
  const isMarketHours = nyHour >= 9 && nyHour < 16;
  const isPreMarket = nyHour >= 4 && nyHour < 9;
  const isAfterHours = nyHour >= 16 && nyHour < 20;
  
  return {
    isOpen: !isWeekend && isMarketHours,
    isPreMarket: !isWeekend && isPreMarket,
    isAfterHours: !isWeekend && isAfterHours,
    isWeekend,
    nyTime: now.toLocaleString('en-US', { 
      timeZone: 'America/New_York',
      weekday: 'short',
      hour: '2-digit',
      minute: '2-digit'
    })
  };
}

async function scrapeYahooQuote(symbol) {
  try {
    const { data } = await fetch(`https://query1.finance.yahoo.com/v8/finance/chart/${symbol}?interval=1d&range=2d`);
    const json = JSON.parse(data);
    const result = json.chart.result[0];
    const meta = result.meta;
    const quotes = result.indicators.quote[0];
    
    const price = meta.regularMarketPrice;
    const prevClose = meta.previousClose || meta.chartPreviousClose;
    const change = price - prevClose;
    const changePct = (change / prevClose) * 100;
    
    return {
      symbol,
      price: price.toFixed(2),
      change: change.toFixed(2),
      changePct: changePct.toFixed(2),
      volume: meta.regularMarketVolume,
      marketState: meta.marketState
    };
  } catch (e) {
    return { symbol, error: e.message };
  }
}

async function getQuotes(symbols) {
  const results = await Promise.allSettled(
    symbols.map(s => scrapeYahooQuote(s))
  );
  return results.map(r => r.status === 'fulfilled' ? r.value : { error: r.reason.message });
}

async function searchNews(query, count = 5) {
  // Use DuckDuckGo news (no API key needed)
  try {
    const encodedQuery = encodeURIComponent(query + ' stock market');
    const { data } = await fetch(`https://html.duckduckgo.com/html/?q=${encodedQuery}&t=h_&iar=news&ia=news`);
    
    // Parse results from HTML (basic extraction)
    const results = [];
    const linkRegex = /<a[^>]+class="result__a"[^>]*href="([^"]+)"[^>]*>([^<]+)<\/a>/gi;
    const snippetRegex = /<a[^>]+class="result__snippet"[^>]*>([^<]+)<\/a>/gi;
    
    let match;
    while ((match = linkRegex.exec(data)) !== null && results.length < count) {
      // Extract actual URL from DuckDuckGo redirect
      let url = match[1];
      const uddgMatch = url.match(/uddg=([^&]+)/);
      if (uddgMatch) {
        url = decodeURIComponent(uddgMatch[1]);
      }
      
      results.push({
        title: match[2].replace(/&amp;/g, '&').replace(/&quot;/g, '"').trim(),
        url: url
      });
    }
    
    return results;
  } catch (e) {
    return [{ error: e.message }];
  }
}

// ─────────────────────────────────────────────────────────────
// Formatting
// ─────────────────────────────────────────────────────────────

function formatQuote(q) {
  if (q.error) return `${q.symbol}: ⚠️ ${q.error}`;
  const arrow = parseFloat(q.changePct) >= 0 ? '📈' : '📉';
  const sign = parseFloat(q.change) >= 0 ? '+' : '';
  return `${q.symbol}: $${q.price} ${arrow} ${sign}${q.changePct}%`;
}

function formatFearGreed(fg) {
  if (fg.error) return `Fear & Greed: ⚠️ unavailable`;
  
  const emoji = fg.score <= 25 ? '😨' : 
                fg.score <= 45 ? '😟' :
                fg.score <= 55 ? '😐' :
                fg.score <= 75 ? '😊' : '🤑';
  
  const trend = fg.score > fg.previous ? '↑' : fg.score < fg.previous ? '↓' : '→';
  
  return `Fear & Greed: ${emoji} ${fg.score}/100 (${fg.rating}) ${trend}`;
}

function formatMarketStatus(ms) {
  if (ms.isOpen) return `🟢 Market OPEN (${ms.nyTime} NY)`;
  if (ms.isPreMarket) return `🟡 Pre-Market (${ms.nyTime} NY)`;
  if (ms.isAfterHours) return `🟠 After Hours (${ms.nyTime} NY)`;
  if (ms.isWeekend) return `⚫ Weekend (${ms.nyTime} NY)`;
  return `🔴 Market Closed (${ms.nyTime} NY)`;
}

// ─────────────────────────────────────────────────────────────
// Main
// ─────────────────────────────────────────────────────────────

async function generateBriefing(options = {}) {
  console.error('📊 Gathering market intelligence...\n');
  
  const [fearGreed, marketStatus, indexQuotes, semiQuotes, nvdaNews] = await Promise.all([
    getFearGreedIndex(),
    getMarketStatus(),
    getQuotes(WATCHLIST.indices),
    getQuotes(WATCHLIST.semiconductors),
    searchNews('NVIDIA semiconductor AI', 4)
  ]);
  
  if (options.json) {
    return JSON.stringify({
      timestamp: new Date().toISOString(),
      marketStatus,
      fearGreed,
      indices: indexQuotes,
      semiconductors: semiQuotes,
      news: nvdaNews
    }, null, 2);
  }
  
  // Build text briefing
  const lines = [];
  const divider = '─'.repeat(36);
  
  lines.push('🎯 **MARKET INTELLIGENCE BRIEFING**');
  lines.push(`📅 ${new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}`);
  lines.push('');
  
  // Market Status
  lines.push(formatMarketStatus(marketStatus));
  lines.push(formatFearGreed(fearGreed));
  lines.push('');
  
  // Indices
  lines.push('**📊 Major Indices**');
  for (const q of indexQuotes) {
    lines.push(formatQuote(q));
  }
  lines.push('');
  
  // Semiconductors
  lines.push('**🔬 Semiconductors**');
  for (const q of semiQuotes) {
    lines.push(formatQuote(q));
  }
  lines.push('');
  
  // Quick summary
  if (!options.quick) {
    // News
    lines.push('**📰 Semiconductor News**');
    for (const article of nvdaNews.slice(0, 4)) {
      if (article.error) {
        lines.push(`• ⚠️ News unavailable`);
      } else {
        lines.push(`• ${article.title}`);
      }
    }
    lines.push('');
  }
  
  // Highlight NVDA specifically
  const nvda = semiQuotes.find(q => q.symbol === 'NVDA');
  if (nvda && !nvda.error) {
    const sentiment = parseFloat(nvda.changePct) > 1 ? '🚀' :
                      parseFloat(nvda.changePct) > 0 ? '✅' :
                      parseFloat(nvda.changePct) > -1 ? '⚠️' : '🔻';
    lines.push(`**🎮 NVDA Spotlight:** $${nvda.price} (${nvda.changePct > 0 ? '+' : ''}${nvda.changePct}%) ${sentiment}`);
  }
  
  lines.push('');
  lines.push(`_Generated by Alyosha 🕯️_`);
  
  return lines.join('\n');
}

// CLI
async function main() {
  const args = process.argv.slice(2);
  const options = {
    json: args.includes('--json'),
    quick: args.includes('--quick')
  };
  
  try {
    const briefing = await generateBriefing(options);
    console.log(briefing);
  } catch (e) {
    console.error('Error generating briefing:', e.message);
    process.exit(1);
  }
}

main();
