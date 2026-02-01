---
name: market-pulse
description: Generate audio market briefings with TTS. Use when asked for market updates, morning briefings, or audio summaries of financial news. Combines web research with voice synthesis for podcast-style delivery.
---

# Market Pulse Skill

Generate concise, professional audio market briefings.

## When to Use

- Morning market briefings
- End-of-day market summaries
- Quick audio updates on market movements
- Podcast-style financial content

## Workflow

### 1. Gather Data

Search for current market data:
```
web_search: "S&P 500 Nasdaq Dow today [date]"
web_search: "VIX volatility fear greed index"
web_search: "[specific sector/stock] news today"
```

Key data points to collect:
- Index levels and % changes (S&P 500, Nasdaq, Dow)
- VIX level and trend
- Key movers (earnings, news-driven)
- Macro catalysts (Fed, earnings season, geopolitics)

### 2. Write the Script

Structure (60-90 seconds read time, ~150-200 words):

```
Opening: "Good [morning/afternoon]. Here's your market pulse for [day, date]."

Headline: What happened? (1-2 sentences on index moves)

Why: The driver behind the move (yields, earnings, macro event)

Context: Bigger picture - week/month trend, what it means

Forward look: 1-2 things to watch

Actionable: Brief portfolio implication (optional)

Close: "That's your market pulse. [Sign-off]"
```

### 3. Generate Audio

Use TTS tool:
```
tts(text="[script]", channel="telegram")
```

Save output to `reports/market-pulse-[date].opus`

### 4. Deliver

Send audio directly via message tool, or present the MEDIA path.

## Style Guidelines

- **Conversational but authoritative** — like a smart friend who works in finance
- **No jargon without context** — explain terms briefly if needed
- **Numbers are specific** — "down four-tenths of a percent" not "slightly down"
- **Always actionable** — what does this mean for the listener?
- **Time-aware** — morning vs evening briefing tone differs

## Example Output

See `references/example-briefing.md` for a sample script.

## Customization

Adjust for audience:
- **Casual**: More personality, simpler language
- **Professional**: Denser data, sector-specific focus
- **Quick hit**: 30 seconds, just the headline + one insight
