#!/usr/bin/env node
/**
 * Watchlist Intelligence Tool
 * 
 * Aggregates news and sentiment for a stock watchlist.
 * Produces actionable briefings for traders/investors.
 * 
 * Usage: node intel.js [--ticker NVDA] [--json] [--brief]
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

// === Configuration ===
const CONFIG_PATH = path.join(__dirname, 'watchlist.json');
const CACHE_DIR = path.join(__dirname, '.cache');

// Ensure cache directory exists
if (!fs.existsSync(CACHE_DIR)) {
  fs.mkdirSync(CACHE_DIR, { recursive: true });
}

// === Sentiment Analysis ===
const POSITIVE_WORDS = new Set([
  'surge', 'soar', 'rally', 'gain', 'jump', 'rise', 'climb', 'beat', 'exceed',
  'strong', 'bullish', 'upgrade', 'buy', 'outperform', 'record', 'high', 'growth',
  'profit', 'revenue', 'success', 'breakthrough', 'innovation', 'partnership',
  'demand', 'boost', 'momentum', 'optimistic', 'positive', 'upside', 'breakout'
]);

const NEGATIVE_WORDS = new Set([
  'drop', 'fall', 'plunge', 'sink', 'decline', 'slide', 'crash', 'miss', 'weak',
  'bearish', 'downgrade', 'sell', 'underperform', 'low', 'loss', 'concern', 'risk',
  'warning', 'delay', 'issue', 'problem', 'lawsuit', 'investigation', 'cut',
  'layoff', 'disappointing', 'negative', 'downside', 'fear', 'worry', 'slump'
]);

function analyzeSentiment(text) {
  const words = text.toLowerCase().split(/\W+/);
  let positive = 0;
  let negative = 0;
  
  for (const word of words) {
    if (POSITIVE_WORDS.has(word)) positive++;
    if (NEGATIVE_WORDS.has(word)) negative++;
  }
  
  const total = positive + negative;
  if (total === 0) return { score: 0, label: 'neutral', confidence: 0 };
  
  const score = (positive - negative) / total;
  const confidence = Math.min(total / 5, 1); // More keywords = higher confidence
  
  let label = 'neutral';
  if (score > 0.3) label = 'bullish';
  else if (score < -0.3) label = 'bearish';
  
  return { score: Math.round(score * 100) / 100, label, confidence: Math.round(confidence * 100) / 100 };
}

// === News Fetching (via Brave Search simulation) ===
// In production, this would use the actual Brave API
// For demo, we'll structure the expected data format

async function fetchNews(ticker, name) {
  // This creates a structured query for the stock
  const query = `${ticker} ${name} stock news`;
  const cacheFile = path.join(CACHE_DIR, `${ticker}-${Date.now() - (Date.now() % 3600000)}.json`);
  
  // Check cache (1 hour TTL)
  if (fs.existsSync(cacheFile)) {
    try {
      return JSON.parse(fs.readFileSync(cacheFile, 'utf8'));
    } catch (e) {
      // Cache corrupted, continue to fetch
    }
  }
  
  // Return query info for external fetching
  return { needsFetch: true, query, ticker, name };
}

// === Report Generation ===
function generateReport(data, options = {}) {
  const { brief = false, json = false } = options;
  
  if (json) {
    return JSON.stringify(data, null, 2);
  }
  
  let report = [];
  const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19) + ' UTC';
  
  report.push('═══════════════════════════════════════════════════════════');
  report.push('  📊 WATCHLIST INTELLIGENCE BRIEFING');
  report.push(`  Generated: ${timestamp}`);
  report.push('═══════════════════════════════════════════════════════════\n');
  
  // Summary section
  const bullish = data.tickers.filter(t => t.sentiment?.label === 'bullish');
  const bearish = data.tickers.filter(t => t.sentiment?.label === 'bearish');
  
  report.push('📈 QUICK SUMMARY');
  report.push('─────────────────');
  if (bullish.length > 0) {
    report.push(`  🟢 Bullish: ${bullish.map(t => t.symbol).join(', ')}`);
  }
  if (bearish.length > 0) {
    report.push(`  🔴 Bearish: ${bearish.map(t => t.symbol).join(', ')}`);
  }
  report.push('');
  
  // Per-ticker details
  for (const ticker of data.tickers) {
    const emoji = ticker.priority === 'high' ? '⭐' : '○';
    const sentimentEmoji = {
      'bullish': '🟢',
      'bearish': '🔴',
      'neutral': '⚪'
    }[ticker.sentiment?.label] || '⚪';
    
    report.push(`${emoji} ${ticker.symbol} — ${ticker.name}`);
    report.push(`  Sentiment: ${sentimentEmoji} ${ticker.sentiment?.label || 'unknown'} (score: ${ticker.sentiment?.score || 0})`);
    
    if (!brief && ticker.headlines?.length > 0) {
      report.push('  Recent Headlines:');
      for (const headline of ticker.headlines.slice(0, 3)) {
        report.push(`    • ${headline}`);
      }
    }
    report.push('');
  }
  
  report.push('═══════════════════════════════════════════════════════════');
  report.push('  End of Briefing');
  report.push('═══════════════════════════════════════════════════════════');
  
  return report.join('\n');
}

// === Main Entry Point ===
async function main() {
  const args = process.argv.slice(2);
  const options = {
    ticker: null,
    json: args.includes('--json'),
    brief: args.includes('--brief'),
    help: args.includes('--help') || args.includes('-h')
  };
  
  // Parse --ticker argument
  const tickerIdx = args.indexOf('--ticker');
  if (tickerIdx !== -1 && args[tickerIdx + 1]) {
    options.ticker = args[tickerIdx + 1].toUpperCase();
  }
  
  if (options.help) {
    console.log(`
Watchlist Intelligence Tool
===========================

Usage: node intel.js [options]

Options:
  --ticker SYMBOL   Analyze a specific ticker only
  --json            Output as JSON
  --brief           Shorter output (no headlines)
  --help, -h        Show this help

Examples:
  node intel.js                    # Full watchlist briefing
  node intel.js --ticker NVDA      # NVIDIA only
  node intel.js --brief            # Quick summary
  node intel.js --json             # JSON output for automation
`);
    return;
  }
  
  // Load config
  let config;
  try {
    config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
  } catch (e) {
    console.error('Error loading watchlist.json:', e.message);
    process.exit(1);
  }
  
  // Filter tickers if specified
  let tickers = config.tickers;
  if (options.ticker) {
    tickers = tickers.filter(t => t.symbol === options.ticker);
    if (tickers.length === 0) {
      console.error(`Ticker ${options.ticker} not found in watchlist.`);
      process.exit(1);
    }
  }
  
  // Build data structure
  const data = {
    timestamp: new Date().toISOString(),
    tickers: tickers.map(t => ({
      symbol: t.symbol,
      name: t.name,
      priority: t.priority,
      sentiment: null,
      headlines: [],
      needsFetch: true
    }))
  };
  
  // Output for external processor to fill in
  if (process.env.INTEL_MODE === 'queries') {
    // Output queries needed
    const queries = data.tickers.map(t => ({
      symbol: t.symbol,
      query: `${t.symbol} ${t.name} stock news`
    }));
    console.log(JSON.stringify(queries, null, 2));
    return;
  }
  
  // Check for piped input (news data)
  if (!process.stdin.isTTY) {
    let input = '';
    process.stdin.setEncoding('utf8');
    for await (const chunk of process.stdin) {
      input += chunk;
    }
    
    try {
      const newsData = JSON.parse(input);
      
      // Merge news data with tickers
      for (const ticker of data.tickers) {
        const tickerNews = newsData[ticker.symbol];
        if (tickerNews && tickerNews.headlines) {
          ticker.headlines = tickerNews.headlines;
          ticker.needsFetch = false;
          
          // Analyze combined sentiment
          const combinedText = tickerNews.headlines.join(' ');
          ticker.sentiment = analyzeSentiment(combinedText);
        }
      }
    } catch (e) {
      console.error('Error parsing news input:', e.message);
    }
  }
  
  // Generate and output report
  console.log(generateReport(data, options));
}

main().catch(console.error);
