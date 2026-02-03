#!/usr/bin/env python3
"""
Fragility Signals Dashboard
Auto-updated weekly, displays market stress indicators
"""

from flask import Flask, jsonify, render_template_string
import json
from pathlib import Path
from datetime import datetime
import os

app = Flask(__name__)

# Try multiple data locations (handles different deployment setups)
def find_data_dir():
    candidates = [
        Path(__file__).parent.parent.parent / 'data' / 'fragility',  # From app dir
        Path('/opt/render/project/src/data/fragility'),  # Render absolute
        Path.cwd() / 'data' / 'fragility',  # From working dir
        Path(__file__).parent / 'data',  # Local to app
    ]
    for p in candidates:
        if p.exists():
            return p
    return None

DATA_DIR = find_data_dir()

# Embedded sample data for when local data unavailable (Render deployment)
# Updated: 2026-02-03
SAMPLE_DATA = {
    "timestamp": "2026-02-03T08:59:00.000000",
    "signals": {
        "volatility": {
            "vix": {"current": 16.24, "5d_ago": 16.35, "change_pct": -0.7},
            "vvix": {"current": 98.77, "5d_ago": 101.26, "change_pct": -2.5},
            "signal": "✅ Normal"
        },
        "credit": {"note": "Need FRED API key for credit spreads"},
        "concentration": {
            "top7_weight_pct": 47.2,
            "signal": "⚠️ CONCENTRATED",
            "note": "Top 7 stocks as % of S&P 500"
        },
        "curve": {
            "10y_yield": 4.28,
            "3m_yield": 3.58,
            "spread": 0.7,
            "signal": "✅ Normal"
        }
    }
}

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Fragility Signals</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a; color: #e0e0e0; padding: 20px;
            max-width: 800px; margin: 0 auto;
        }
        h1 { color: #fff; margin-bottom: 10px; }
        .subtitle { color: #888; margin-bottom: 30px; }
        .card {
            background: #1a1a1a; border-radius: 12px; padding: 20px;
            margin-bottom: 15px; border: 1px solid #333;
        }
        .signal-row {
            display: flex; justify-content: space-between; align-items: center;
            padding: 12px 0; border-bottom: 1px solid #333;
        }
        .signal-row:last-child { border-bottom: none; }
        .signal-name { font-weight: 500; }
        .signal-value { font-size: 1.2em; font-weight: bold; }
        .status-normal { color: #4ade80; }
        .status-elevated { color: #fbbf24; }
        .status-critical { color: #f87171; }
        .summary {
            background: #1e3a5f; border: 1px solid #3b82f6;
            padding: 15px; border-radius: 8px; margin-top: 20px;
        }
        .timestamp { color: #666; font-size: 0.85em; margin-top: 20px; }
        .demo-banner {
            background: #422006; border: 1px solid #f59e0b;
            padding: 10px; border-radius: 8px; margin-bottom: 20px;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <h1>📊 Fragility Signals</h1>
    <p class="subtitle">Market stress indicators · Updated weekly</p>
    
    {% if demo_mode %}
    <div class="demo-banner">
        ⚠️ Demo mode — showing sample data. Live data updates weekly.
    </div>
    {% endif %}
    
    <div class="card">
        {% for signal in signals %}
        <div class="signal-row">
            <span class="signal-name">{{ signal.name }}</span>
            <span class="signal-value {{ signal.status_class }}">
                {{ signal.value }} {{ signal.status_emoji }}
            </span>
        </div>
        {% endfor %}
    </div>
    
    <div class="summary">
        <strong>{{ summary.count }}/{{ summary.total }}</strong> signals elevated
        {% if summary.count >= 2 %}
        <br>⚠️ Multiple stress signals — increased caution warranted
        {% else %}
        <br>✅ No systemic stress detected
        {% endif %}
    </div>
    
    <p class="timestamp">Last updated: {{ timestamp }}</p>
</body>
</html>
"""

def get_latest_data():
    """Load most recent fragility data, fallback to sample"""
    try:
        if DATA_DIR and DATA_DIR.exists():
            files = sorted(DATA_DIR.glob('*.json'), reverse=True)
            if files:
                with open(files[0]) as f:
                    return json.load(f), files[0].stem, False
    except Exception as e:
        app.logger.error(f"Error loading data: {e}")
    
    # Fallback to sample data
    return SAMPLE_DATA, SAMPLE_DATA["timestamp"][:10], True

def format_signals(data):
    """Format signals for display"""
    if not data:
        return [], {"count": 0, "total": 0}
    
    signals = []
    elevated = 0
    
    s = data.get("signals", {})
    
    # VIX
    vix = s.get("volatility", {}).get("vix", {})
    vix_val = vix.get("current", 0)
    is_elevated = vix_val >= 20
    signals.append({
        "name": "VIX",
        "value": vix_val if vix_val else "N/A",
        "status_emoji": "⚠️" if is_elevated else "✅",
        "status_class": "status-elevated" if is_elevated else "status-normal"
    })
    if is_elevated:
        elevated += 1
    
    # VVIX
    vvix = s.get("volatility", {}).get("vvix", {})
    vvix_val = vvix.get("current", 0)
    is_elevated = vvix_val > 110
    signals.append({
        "name": "VVIX (Vol of Vol)",
        "value": vvix_val if vvix_val else "N/A",
        "status_emoji": "⚠️" if is_elevated else "✅",
        "status_class": "status-elevated" if is_elevated else "status-normal"
    })
    if is_elevated:
        elevated += 1
    
    # Concentration
    conc = s.get("concentration", {})
    conc_val = conc.get("top7_weight_pct", 0)
    is_elevated = conc_val > 40
    signals.append({
        "name": "Top 7 Concentration",
        "value": f"{conc_val}%" if conc_val else "N/A",
        "status_emoji": "⚠️" if is_elevated else "✅",
        "status_class": "status-elevated" if is_elevated else "status-normal"
    })
    if is_elevated:
        elevated += 1
    
    # Yield Curve
    curve = s.get("curve", {})
    spread = curve.get("spread", 0)
    is_inverted = spread < 0
    signals.append({
        "name": "Yield Curve (10Y-3M)",
        "value": f"{spread:+.2f}%" if spread else "N/A",
        "status_emoji": "🔴" if is_inverted else "✅",
        "status_class": "status-critical" if is_inverted else "status-normal"
    })
    if is_inverted:
        elevated += 1
    
    return signals, {"count": elevated, "total": len(signals)}

@app.route('/')
def index():
    data, timestamp, demo_mode = get_latest_data()
    signals, summary = format_signals(data)
    return render_template_string(
        TEMPLATE,
        signals=signals,
        summary=summary,
        timestamp=timestamp,
        demo_mode=demo_mode
    )

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/api/data')
def api_data():
    data, timestamp, demo_mode = get_latest_data()
    return jsonify({
        "data": data,
        "timestamp": timestamp,
        "demo_mode": demo_mode
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
