#!/usr/bin/env python3
"""
Prediction Calibration Tracker
==============================

Track predictions, outcomes, and measure calibration over time.
Talebian tool: forces explicit uncertainty quantification.

Usage:
    python3 prediction-tracker.py add                    # Add new prediction
    python3 prediction-tracker.py list [--pending]       # List predictions
    python3 prediction-tracker.py resolve <id>           # Resolve a prediction
    python3 prediction-tracker.py stats                  # Calibration analysis
    python3 prediction-tracker.py due                    # Show predictions due for resolution

Data stored in: memory/predictions.jsonl
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import uuid

PREDICTIONS_FILE = Path.home() / '.openclaw/workspace/memory/predictions.jsonl'

DOMAINS = ['markets', 'geopolitics', 'tech', 'ai', 'personal', 'science', 'other']


def load_predictions():
    predictions = []
    if not PREDICTIONS_FILE.exists():
        return predictions
    with open(PREDICTIONS_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    predictions.append(json.loads(line))
                except:
                    continue
    return predictions


def save_prediction(pred):
    with open(PREDICTIONS_FILE, 'a') as f:
        f.write(json.dumps(pred) + '\n')


def save_all(predictions):
    with open(PREDICTIONS_FILE, 'w') as f:
        for p in predictions:
            f.write(json.dumps(p) + '\n')


def add_prediction():
    print("📝 New Prediction\n")
    
    text = input("Prediction: ").strip()
    if not text:
        print("❌ Prediction text required")
        return
    
    confidence = input("Confidence % (50-99): ").strip()
    try:
        confidence = int(confidence)
        if confidence < 50 or confidence > 99:
            print("⚠️ Confidence should be 50-99%, setting to 70%")
            confidence = 70
    except:
        confidence = 70
    
    print(f"Domains: {', '.join(DOMAINS)}")
    domain = input("Domain: ").strip().lower()
    if domain not in DOMAINS:
        domain = 'other'
    
    resolve_by = input("Resolve by (YYYY-MM-DD or days from now, e.g. '30'): ").strip()
    try:
        if resolve_by.isdigit():
            resolve_date = (datetime.now() + timedelta(days=int(resolve_by))).strftime('%Y-%m-%d')
        else:
            datetime.strptime(resolve_by, '%Y-%m-%d')
            resolve_date = resolve_by
    except:
        resolve_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        print(f"⚠️ Invalid date, defaulting to {resolve_date}")
    
    rationale = input("Rationale (why this confidence?): ").strip()
    
    pred = {
        'id': str(uuid.uuid4())[:8],
        'text': text,
        'confidence': confidence,
        'domain': domain,
        'created': datetime.now().strftime('%Y-%m-%d'),
        'resolve_by': resolve_date,
        'rationale': rationale,
        'resolved': False,
        'outcome': None,
        'post_mortem': None
    }
    
    save_prediction(pred)
    print(f"\n✅ Prediction logged (id: {pred['id']})")
    print(f"   {confidence}%: {text}")
    print(f"   Resolve by: {resolve_date}")


def add_prediction_direct(text, confidence, domain, resolve_by, rationale=""):
    """Add prediction programmatically."""
    if isinstance(resolve_by, int):
        resolve_date = (datetime.now() + timedelta(days=resolve_by)).strftime('%Y-%m-%d')
    else:
        resolve_date = resolve_by
    
    pred = {
        'id': str(uuid.uuid4())[:8],
        'text': text,
        'confidence': min(99, max(50, confidence)),
        'domain': domain if domain in DOMAINS else 'other',
        'created': datetime.now().strftime('%Y-%m-%d'),
        'resolve_by': resolve_date,
        'rationale': rationale,
        'resolved': False,
        'outcome': None,
        'post_mortem': None
    }
    save_prediction(pred)
    return pred


def list_predictions(pending_only=False):
    predictions = load_predictions()
    
    if pending_only:
        predictions = [p for p in predictions if not p.get('resolved')]
    
    if not predictions:
        print("📭 No predictions" + (" pending" if pending_only else ""))
        return
    
    print(f"📋 Predictions ({len(predictions)})\n")
    
    for p in sorted(predictions, key=lambda x: x.get('resolve_by', '')):
        status = "✅" if p.get('outcome') == 'right' else "❌" if p.get('outcome') == 'wrong' else "⏳"
        conf = p.get('confidence', '?')
        text = p.get('text', '')[:50]
        resolve = p.get('resolve_by', '?')
        pid = p.get('id', '?')
        
        print(f"{status} [{pid}] {conf}%: {text}...")
        print(f"   Domain: {p.get('domain')} | Resolve: {resolve}")
        print()


def resolve_prediction(pred_id):
    predictions = load_predictions()
    
    found = None
    for p in predictions:
        if p.get('id') == pred_id:
            found = p
            break
    
    if not found:
        print(f"❌ Prediction {pred_id} not found")
        return
    
    print(f"Resolving: {found.get('text')}")
    print(f"Confidence was: {found.get('confidence')}%")
    print()
    
    outcome = input("Outcome (right/wrong/partial): ").strip().lower()
    if outcome not in ['right', 'wrong', 'partial']:
        outcome = 'partial'
    
    post_mortem = input("Post-mortem (what did you learn?): ").strip()
    
    found['resolved'] = True
    found['outcome'] = outcome
    found['post_mortem'] = post_mortem
    found['resolved_date'] = datetime.now().strftime('%Y-%m-%d')
    
    save_all(predictions)
    
    emoji = {'right': '✅', 'wrong': '❌', 'partial': '🟡'}[outcome]
    print(f"\n{emoji} Prediction resolved as: {outcome}")


def show_due():
    predictions = load_predictions()
    today = datetime.now().strftime('%Y-%m-%d')
    
    due = [p for p in predictions 
           if not p.get('resolved') and p.get('resolve_by', '9999') <= today]
    
    upcoming = [p for p in predictions
                if not p.get('resolved') 
                and today < p.get('resolve_by', '9999') <= (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')]
    
    if due:
        print(f"🔴 DUE NOW ({len(due)})\n")
        for p in due:
            print(f"   [{p['id']}] {p['confidence']}%: {p['text'][:50]}...")
        print()
    
    if upcoming:
        print(f"🟡 Due within 7 days ({len(upcoming)})\n")
        for p in upcoming:
            print(f"   [{p['id']}] {p['resolve_by']}: {p['text'][:50]}...")
        print()
    
    if not due and not upcoming:
        print("✅ No predictions due soon")


def calculate_stats():
    predictions = load_predictions()
    resolved = [p for p in predictions if p.get('resolved')]
    
    if len(resolved) < 5:
        print(f"📊 Need more data ({len(resolved)}/5 resolved predictions)")
        print("   Keep making predictions!")
        return
    
    # Calibration by confidence bucket
    buckets = defaultdict(lambda: {'right': 0, 'total': 0})
    
    for p in resolved:
        conf = p.get('confidence', 70)
        outcome = p.get('outcome')
        
        # Round to nearest 10
        bucket = round(conf / 10) * 10
        buckets[bucket]['total'] += 1
        if outcome == 'right':
            buckets[bucket]['right'] += 1
        elif outcome == 'partial':
            buckets[bucket]['right'] += 0.5
    
    # Domain stats
    domain_stats = defaultdict(lambda: {'right': 0, 'total': 0})
    for p in resolved:
        domain = p.get('domain', 'other')
        domain_stats[domain]['total'] += 1
        if p.get('outcome') == 'right':
            domain_stats[domain]['right'] += 1
        elif p.get('outcome') == 'partial':
            domain_stats[domain]['right'] += 0.5
    
    # Brier score
    brier = 0
    for p in resolved:
        conf = p.get('confidence', 70) / 100
        outcome = 1 if p.get('outcome') == 'right' else 0.5 if p.get('outcome') == 'partial' else 0
        brier += (conf - outcome) ** 2
    brier = brier / len(resolved)
    
    print(f"📊 Calibration Analysis ({len(resolved)} predictions)\n")
    
    print("**Calibration by Confidence:**")
    print("   Stated → Actual")
    for bucket in sorted(buckets.keys()):
        stats = buckets[bucket]
        actual = stats['right'] / stats['total'] * 100 if stats['total'] > 0 else 0
        n = stats['total']
        diff = actual - bucket
        indicator = "✅" if abs(diff) < 10 else "⚠️" if diff > 0 else "🔻"
        print(f"   {bucket}% → {actual:.0f}% (n={n}) {indicator}")
    
    print(f"\n**Brier Score:** {brier:.3f}")
    print(f"   (0 = perfect, 0.25 = random, lower is better)")
    
    print("\n**By Domain:**")
    for domain, stats in sorted(domain_stats.items(), key=lambda x: -x[1]['total']):
        if stats['total'] > 0:
            acc = stats['right'] / stats['total'] * 100
            print(f"   {domain}: {acc:.0f}% ({stats['total']} predictions)")
    
    # Overconfidence check
    total_conf = sum(p.get('confidence', 70) for p in resolved) / len(resolved)
    total_actual = sum(1 if p.get('outcome') == 'right' else 0.5 if p.get('outcome') == 'partial' else 0 
                       for p in resolved) / len(resolved) * 100
    
    print(f"\n**Overall:**")
    print(f"   Average confidence: {total_conf:.0f}%")
    print(f"   Actual accuracy: {total_actual:.0f}%")
    if total_conf > total_actual + 10:
        print(f"   ⚠️ You may be overconfident by ~{total_conf - total_actual:.0f}%")
    elif total_actual > total_conf + 10:
        print(f"   💡 You may be underconfident by ~{total_actual - total_conf:.0f}%")
    else:
        print(f"   ✅ Well calibrated!")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'add':
        add_prediction()
    elif cmd == 'list':
        pending = '--pending' in sys.argv
        list_predictions(pending_only=pending)
    elif cmd == 'resolve' and len(sys.argv) >= 3:
        resolve_prediction(sys.argv[2])
    elif cmd == 'stats':
        calculate_stats()
    elif cmd == 'due':
        show_due()
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
