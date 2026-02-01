#!/usr/bin/env python3
"""
Log a forecast to the tracker CSV.
Usage: python3 log-forecast.py "2026-02-01" "markets" "Bearish on tech short-term" "65" "bearish" "1week"
"""
import sys
import csv
from pathlib import Path

TRACKER = Path(__file__).parent.parent / "memory/forecasts/tracker.csv"

def log_forecast(date, domain, prediction, confidence, direction, horizon):
    with open(TRACKER, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([date, domain, prediction, confidence, direction, horizon, "", "", ""])
    print(f"✓ Logged forecast: {domain} - {prediction[:50]}...")

def update_outcome(date, domain, outcome, accuracy_notes=""):
    """Update outcome for a past forecast"""
    rows = []
    updated = False
    with open(TRACKER, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 6 and row[0] == date and row[1] == domain and not row[6]:
                row[6] = outcome
                row[7] = str(__import__('datetime').date.today())
                row[8] = accuracy_notes
                updated = True
            rows.append(row)
    
    if updated:
        with open(TRACKER, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        print(f"✓ Updated outcome for {date} {domain}: {outcome}")
    else:
        print(f"✗ No matching forecast found for {date} {domain}")

if __name__ == "__main__":
    if len(sys.argv) >= 7:
        log_forecast(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
    elif len(sys.argv) >= 5 and sys.argv[1] == "--outcome":
        update_outcome(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] if len(sys.argv) > 5 else "")
    else:
        print("Usage:")
        print("  Log:    python3 log-forecast.py DATE DOMAIN PREDICTION CONFIDENCE DIRECTION HORIZON")
        print("  Update: python3 log-forecast.py --outcome DATE DOMAIN OUTCOME [NOTES]")
