#!/usr/bin/env python3
"""
Deep Analyst Runner
===================

Runs the full stock analysis framework and outputs structured data
for the Deep Analyst agent to synthesize.

Usage:
    python3 scripts/deep-analyst-runner.py TICKER

This script is called BY the Deep Analyst agent (not directly by cron).
It collects all data using Jon's 7-dimension framework + FMP fundamentals.
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / '.openclaw/workspace'
SCRIPTS = WORKSPACE / 'scripts'


def run_tool(cmd, name, timeout=60):
    """Run a tool and capture output."""
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            cwd=WORKSPACE
        )
        if result.returncode == 0:
            return {"status": "ok", "output": result.stdout}
        else:
            return {"status": "error", "output": result.stderr[:500]}
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "output": f"Timeout after {timeout}s"}
    except Exception as e:
        return {"status": "error", "output": str(e)}


def deep_analysis(ticker: str) -> dict:
    """Run full analysis framework on ticker."""
    ticker = ticker.upper()
    
    print(f"{'='*60}")
    print(f"DEEP ANALYST FRAMEWORK — {ticker}")
    print(f"{'='*60}")
    print(f"Started: {datetime.utcnow().isoformat()}")
    print()
    
    results = {
        "ticker": ticker,
        "timestamp": datetime.utcnow().isoformat(),
        "dimensions": {}
    }
    
    # === DIMENSION 1-2: Transcript Analysis ===
    print("📊 [1/6] Transcript tone trends...")
    results["dimensions"]["transcript_trends"] = run_tool(
        ['python3', str(SCRIPTS / 'transcript-compare.py'), ticker, '--quarters', '4'],
        "transcript_trends",
        timeout=90
    )
    
    print("📊 [2/6] Deep transcript signals...")
    results["dimensions"]["transcript_deep"] = run_tool(
        ['python3', str(SCRIPTS / 'deep-analyzer.py'), ticker, '--transcript'],
        "transcript_deep",
        timeout=90
    )
    
    # === DIMENSION 3: Insider Activity ===
    print("📊 [3/6] Insider activity...")
    results["dimensions"]["insider"] = run_tool(
        ['python3', str(SCRIPTS / 'finnhub-client.py'), 'insider', ticker],
        "insider"
    )
    
    # === DIMENSION 4: Analyst Sentiment ===
    print("📊 [4/6] Analyst sentiment...")
    results["dimensions"]["analyst"] = run_tool(
        ['python3', str(SCRIPTS / 'finnhub-client.py'), 'recommend', ticker],
        "analyst"
    )
    
    # === FUNDAMENTALS: FMP Full Analysis ===
    print("📊 [5/6] FMP fundamentals snapshot...")
    results["dimensions"]["fundamentals"] = run_tool(
        ['python3', str(SCRIPTS / 'fmp-client.py'), 'snapshot', ticker],
        "fundamentals"
    )
    
    # === VALUATION & PEERS ===
    print("📊 [6/6] Valuation metrics & peers...")
    results["dimensions"]["metrics"] = run_tool(
        ['python3', str(SCRIPTS / 'fmp-client.py'), 'metrics', ticker],
        "metrics"
    )
    
    # === Print Summary ===
    print()
    print("="*60)
    print("DATA COLLECTION COMPLETE")
    print("="*60)
    
    successes = sum(1 for d in results["dimensions"].values() if d["status"] == "ok")
    total = len(results["dimensions"])
    print(f"Success: {successes}/{total} dimensions")
    
    # Print all collected data for the agent to analyze
    print()
    print("="*60)
    print("COLLECTED DATA FOR SYNTHESIS")
    print("="*60)
    
    for dim_name, dim_data in results["dimensions"].items():
        print(f"\n### {dim_name.upper()} ###")
        if dim_data["status"] == "ok":
            # Truncate very long outputs
            output = dim_data["output"]
            if len(output) > 3000:
                output = output[:3000] + "\n... [truncated]"
            print(output)
        else:
            print(f"[{dim_data['status']}] {dim_data['output']}")
    
    print()
    print("="*60)
    print("7-DIMENSION SCORING FRAMEWORK")
    print("="*60)
    print("""
Score each dimension 1-10, then calculate weighted average:

| Dimension        | Weight | What to Assess                              |
|------------------|--------|---------------------------------------------|
| Business Quality | 20%    | Moat, margins, competitive position         |
| Management       | 15%    | Capital allocation, honesty, incentives     |
| Financials       | 20%    | Balance sheet, cash flow, ROE, margins      |
| Valuation        | 15%    | Price vs intrinsic value, vs peers          |
| Technicals       | 10%    | Trend, support/resistance, momentum         |
| Sentiment        | 10%    | Analyst ratings, insider activity, news     |
| Catalyst         | 10%    | Upcoming events, timing, entry trigger      |

SCORING EACH DIMENSION:
- 9-10: Exceptional, among the best
- 7-8: Strong, clearly positive
- 5-6: Average, no edge
- 3-4: Weak, concerning
- 1-2: Poor, red flag

CALCULATE FINAL SCORE:
Final = (BQ×0.20) + (Mgmt×0.15) + (Fin×0.20) + (Val×0.15) + (Tech×0.10) + (Sent×0.10) + (Cat×0.10)

OUTPUT FORMAT (required):
```
DIMENSION SCORES:
- Business Quality: X/10 — [reason]
- Management: X/10 — [reason]
- Financials: X/10 — [reason]
- Valuation: X/10 — [reason]
- Technicals: X/10 — [reason]
- Sentiment: X/10 — [reason]
- Catalyst: X/10 — [reason]

WEIGHTED FINAL SCORE: X.X/10
```

DECISION THRESHOLD: 7.5

If FINAL >= 7.5: Format EXECUTE notification with full trade details
If FINAL < 7.5: Log "TICKER scored X.X - below threshold", stay silent
""")
    
    return results


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nAvailable tickers: Any US stock symbol")
        sys.exit(1)
    
    ticker = sys.argv[1]
    deep_analysis(ticker)


if __name__ == '__main__':
    main()
