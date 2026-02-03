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

DATA_DIR = Path(__file__).parent.parent.parent / 'data' / 'fragility'

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
    </style>
</head>
<body>
    <h1>📊 Fragility Signals</h1>
    <p class="subtitle">Market stress indicators · Updated weekly</p>
    
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
    """Load most recent fragility data"""
    try:
        files = sorted(DATA_DIR.glob('*.json'), reverse=True)
        if files:
            with open(files[0]) as f:
                return json.load(f), files[0].stem
        return None, None
    except:
        return None, None

def format_signals(data):
    """Format signals for display"""
    if not data:
        return [], {"count": 0, "total": 0}
    
    signals = []
    elevated = 0
    
    s = data.get("signals", {})
    
    # VIX
    vix = s.get("volatility", {}).get("vix", {})
    signals.append({
        "name": "VIX",
        "value": vix.get("current", "N/A"),
        "status_emoji": "✅" if vix.get("current", 0) < 20 else "⚠️",
        "status_class": "status-normal" if vix.get("current", 0) < 20 else "status-elevated"
    })
    if vix.get("current", 0) >= 20:
        elevated += 1
    
    # VVIX
    vvix = s.get("volatility", {}).get("vvix", {})
    is_elevated = vvix.get("current", 0) > 110
    signals.append({
        "name": "VVIX (Vol of Vol)",
        "value": vvix.get("current", "N/A"),
        "status_emoji": "⚠️" if is_elevated else "✅",
        "status_class": "status-elevated" if is_elevated else "status-normal"
    })
    if is_elevated:
        elevated += 1
    
    # Concentration
    conc = s.get("concentration", {})
    is_elevated = conc.get("top7_weight_pct", 0) > 40
    signals.append({
        "name": "Top 7 Concentration",
        "value": f"{conc.get('top7_weight_pct', 'N/A')}%",
        "status_emoji": "⚠️" if is_elevated else "✅",
        "status_class": "status-elevated" if is_elevated else "status-normal"
    })
    if is_elevated:
        elevated += 1
    
    # Yield Curve
    curve = s.get("curve", {})
    is_inverted = curve.get("spread", 1) < 0
    signals.append({
        "name": "10Y-3M Spread",
        "value": f"{curve.get('spread', 'N/A')}%",
        "status_emoji": "⚠️" if is_inverted else "✅",
        "status_class": "status-elevated" if is_inverted else "status-normal"
    })
    if is_inverted:
        elevated += 1
    
    return signals, {"count": elevated, "total": 4}

@app.route('/')
def index():
    data, date = get_latest_data()
    signals, summary = format_signals(data)
    return render_template_string(TEMPLATE, 
        signals=signals, 
        summary=summary,
        timestamp=date or "No data"
    )

@app.route('/api/latest')
def api_latest():
    data, date = get_latest_data()
    return jsonify({"data": data, "date": date})

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
