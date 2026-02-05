#!/usr/bin/env python3
"""
Quarterly Calibration Script
Analyzes trade outcomes to validate/adjust scoring weights.

Usage:
  python3 scripts/quarterly-calibration.py           # Full report
  python3 scripts/quarterly-calibration.py --brief   # Summary only
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

TRADE_LOG = Path.home() / ".openclaw/workspace/memory/goals/trading/trade-log.jsonl"
WEIGHTS_FILE = Path.home() / ".openclaw/workspace/memory/goals/trading/learning-weights.json"
MIN_TRADES_FOR_CALIBRATION = 20

def load_trades():
    """Load all trades from log."""
    if not TRADE_LOG.exists():
        return []
    
    trades = []
    with open(TRADE_LOG) as f:
        for line in f:
            if line.strip():
                trades.append(json.loads(line))
    return trades

def load_weights():
    """Load current dimension weights."""
    if WEIGHTS_FILE.exists():
        with open(WEIGHTS_FILE) as f:
            return json.load(f)
    return {}

def analyze_score_buckets(trades):
    """Win rate by score bucket."""
    buckets = defaultdict(lambda: {"wins": 0, "losses": 0, "total": 0})
    
    for t in trades:
        if t.get("outcome") is None:
            continue
        
        score = t.get("final_score", 0)
        bucket = f"{int(score)}.0-{int(score)}.9"
        
        buckets[bucket]["total"] += 1
        if t["outcome"].get("pnl_pct", 0) > 0:
            buckets[bucket]["wins"] += 1
        else:
            buckets[bucket]["losses"] += 1
    
    return dict(buckets)

def analyze_dimensions(trades):
    """Which dimensions correlate with wins?"""
    dimension_performance = defaultdict(lambda: {"win_avg": [], "loss_avg": []})
    
    for t in trades:
        if t.get("outcome") is None or "dimension_scores" not in t:
            continue
        
        is_win = t["outcome"].get("pnl_pct", 0) > 0
        
        for dim, score in t["dimension_scores"].items():
            if is_win:
                dimension_performance[dim]["win_avg"].append(score)
            else:
                dimension_performance[dim]["loss_avg"].append(score)
    
    # Calculate averages and delta
    results = {}
    for dim, data in dimension_performance.items():
        win_avg = sum(data["win_avg"]) / len(data["win_avg"]) if data["win_avg"] else 0
        loss_avg = sum(data["loss_avg"]) / len(data["loss_avg"]) if data["loss_avg"] else 0
        results[dim] = {
            "win_avg": round(win_avg, 2),
            "loss_avg": round(loss_avg, 2),
            "delta": round(win_avg - loss_avg, 2),  # Higher = more predictive
            "samples": len(data["win_avg"]) + len(data["loss_avg"])
        }
    
    return results

def suggest_weight_adjustments(dimension_analysis, current_weights):
    """Suggest weight changes based on predictive power."""
    suggestions = []
    
    # Sort by delta (predictive power)
    sorted_dims = sorted(
        dimension_analysis.items(), 
        key=lambda x: abs(x[1]["delta"]), 
        reverse=True
    )
    
    for dim, data in sorted_dims:
        current = current_weights.get("dimensions", {}).get(dim, {}).get("weight", 0.15)
        
        if data["delta"] > 1.0 and data["samples"] >= 10:
            # Strong predictor, suggest increase
            suggestions.append({
                "dimension": dim,
                "current_weight": current,
                "suggested": min(current + 0.05, 0.30),
                "reason": f"Strong predictor (delta +{data['delta']})"
            })
        elif data["delta"] < -0.5 and data["samples"] >= 10:
            # Counter-predictive, suggest decrease
            suggestions.append({
                "dimension": dim,
                "current_weight": current,
                "suggested": max(current - 0.05, 0.05),
                "reason": f"Counter-predictive (delta {data['delta']})"
            })
    
    return suggestions

def calculate_overall_stats(trades):
    """Overall performance stats."""
    closed = [t for t in trades if t.get("outcome") is not None]
    if not closed:
        return None
    
    wins = sum(1 for t in closed if t["outcome"].get("pnl_pct", 0) > 0)
    total_pnl = sum(t["outcome"].get("pnl_pct", 0) for t in closed)
    
    return {
        "total_trades": len(trades),
        "closed_trades": len(closed),
        "pending": len(trades) - len(closed),
        "win_rate": round(wins / len(closed) * 100, 1) if closed else 0,
        "avg_return": round(total_pnl / len(closed), 2) if closed else 0,
        "total_return": round(total_pnl, 2)
    }

def generate_report(brief=False):
    """Generate calibration report."""
    trades = load_trades()
    weights = load_weights()
    
    if not trades:
        return "📊 **Quarterly Calibration**\n\nNo trades logged yet. Start trading to build data."
    
    stats = calculate_overall_stats(trades)
    closed_count = stats["closed_trades"] if stats else 0
    
    report = [f"📊 **Quarterly Calibration Report**"]
    report.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC*\n")
    
    # Overall stats
    if stats:
        report.append("**Overall Performance**")
        report.append(f"• Trades: {stats['total_trades']} ({stats['closed_trades']} closed, {stats['pending']} pending)")
        if closed_count > 0:
            report.append(f"• Win rate: {stats['win_rate']}%")
            report.append(f"• Avg return: {stats['avg_return']}%")
        report.append("")
    
    # Check if enough data
    if closed_count < MIN_TRADES_FOR_CALIBRATION:
        report.append(f"⚠️ **Insufficient data for calibration**")
        report.append(f"Need {MIN_TRADES_FOR_CALIBRATION} closed trades, have {closed_count}.")
        report.append(f"Collecting data... ({closed_count}/{MIN_TRADES_FOR_CALIBRATION})")
        return "\n".join(report)
    
    if brief:
        return "\n".join(report)
    
    # Score bucket analysis
    buckets = analyze_score_buckets(trades)
    if buckets:
        report.append("**Win Rate by Score**")
        for bucket in sorted(buckets.keys()):
            data = buckets[bucket]
            wr = round(data["wins"] / data["total"] * 100, 1) if data["total"] else 0
            report.append(f"• {bucket}: {wr}% ({data['wins']}/{data['total']})")
        report.append("")
    
    # Dimension analysis
    dim_analysis = analyze_dimensions(trades)
    if dim_analysis:
        report.append("**Dimension Predictive Power**")
        sorted_dims = sorted(dim_analysis.items(), key=lambda x: x[1]["delta"], reverse=True)
        for dim, data in sorted_dims:
            indicator = "🟢" if data["delta"] > 0.5 else "🟡" if data["delta"] > 0 else "🔴"
            report.append(f"• {indicator} {dim}: delta {data['delta']:+.2f} (win avg {data['win_avg']}, loss avg {data['loss_avg']})")
        report.append("")
    
    # Weight suggestions
    suggestions = suggest_weight_adjustments(dim_analysis, weights)
    if suggestions:
        report.append("**Suggested Weight Adjustments**")
        for s in suggestions:
            report.append(f"• {s['dimension']}: {s['current_weight']:.0%} → {s['suggested']:.0%}")
            report.append(f"  _{s['reason']}_")
        report.append("")
        report.append("_Review suggestions manually before applying._")
    else:
        report.append("✅ **No weight adjustments recommended**")
        report.append("Current weights performing as expected.")
    
    return "\n".join(report)

if __name__ == "__main__":
    brief = "--brief" in sys.argv
    print(generate_report(brief=brief))
