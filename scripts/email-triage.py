#!/usr/bin/env python3
"""
Email Triage Tool
=================

Scans inbox, categorizes emails, and generates a priority digest.

Usage:
    python3 email-triage.py              # Full scan
    python3 email-triage.py --unread     # Unread only
    python3 email-triage.py --hours 6    # Last 6 hours
    python3 email-triage.py --summary    # Just the digest
    python3 email-triage.py vip add "person@email.com"   # Add VIP sender
    python3 email-triage.py vip list                     # List VIP senders
    python3 email-triage.py vip remove "person@email.com" # Remove VIP

Categories:
    🔴 URGENT    - Action required, time-sensitive
    🟠 IMPORTANT - Worth reading, personal or business (includes VIPs)
    🔵 INFO      - Newsletters, updates (can batch-read)
    ⚪ LOW       - Promotions, notifications (can ignore)
"""

import subprocess
import json
import re
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from pathlib import Path

# =============================================================================
# Configuration
# =============================================================================

VIP_CONFIG_FILE = Path.home() / '.openclaw/workspace/memory/email-vip-senders.json'

def load_vip_senders() -> List[str]:
    """Load VIP senders from config file."""
    if VIP_CONFIG_FILE.exists():
        try:
            with open(VIP_CONFIG_FILE) as f:
                data = json.load(f)
                return data.get('vip_senders', [])
        except:
            pass
    return []

def save_vip_senders(senders: List[str]):
    """Save VIP senders to config file."""
    VIP_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(VIP_CONFIG_FILE, 'w') as f:
        json.dump({'vip_senders': senders, 'updated': datetime.now().isoformat()}, f, indent=2)

URGENT_SENDERS = [
    # Add specific senders that should always be flagged urgent
]

URGENT_KEYWORDS = [
    "urgent", "asap", "immediately", "action required", "deadline",
    "overdue", "expiring", "final notice", "security alert"
]

IMPORTANT_SENDERS = [
    # Personal contacts or key business emails
    "@google.com",      # Google account security
    "@github.com",      # Code-related
    "noreply@medium.com",
]

NEWSLETTER_SENDERS = [
    "substack.com",
    "newsletter",
    "digest",
    "weekly",
    "morning brew",
    "the hustle",
]

LOW_PRIORITY_SENDERS = [
    "no-reply",
    "noreply",
    "marketing",
    "promotions",
    "amazon.com",
    "flippa",
    "notifications",
]

# =============================================================================
# Email Fetching (via Himalaya)
# =============================================================================

def run_himalaya(args: List[str]) -> str:
    """Run himalaya command and return output."""
    cmd = ["himalaya"] + args + ["--account", "gmail"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout + result.stderr

def list_emails(folder: str = "INBOX", count: int = 20) -> List[Dict]:
    """List recent emails from folder."""
    # himalaya v1.x: options come after subcommand
    result = subprocess.run(
        ["himalaya", "envelope", "list", 
         "--folder", folder, "--page-size", str(count),
         "--account", "gmail"],
        capture_output=True, text=True
    )
    output = result.stdout + result.stderr
    return parse_table_output(output)

def parse_table_output(output: str) -> List[Dict]:
    """Parse himalaya table output if JSON fails."""
    emails = []
    lines = output.strip().split('\n')
    
    for line in lines:
        if line.startswith('|') and not line.startswith('| ID'):
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 4:
                emails.append({
                    'id': parts[0],
                    'flags': parts[1],
                    'subject': parts[2] if len(parts) > 2 else '',
                    'from': parts[3] if len(parts) > 3 else '',
                    'date': parts[4] if len(parts) > 4 else '',
                })
    
    return emails

def get_email_body(email_id: str) -> str:
    """Get email body text."""
    output = run_himalaya(["message", "read", email_id])
    return output[:2000]  # Truncate for safety

# =============================================================================
# Email Classification
# =============================================================================

def classify_email(email: Dict, vip_senders: List[str] = None) -> Tuple[str, str]:
    """
    Classify email into category and return (category, reason).
    
    Returns:
        ('URGENT', 'reason'), ('IMPORTANT', 'reason'), 
        ('INFO', 'reason'), ('LOW', 'reason')
    """
    subject = email.get('subject', '').lower()
    sender = email.get('from', '').lower()
    flags = email.get('flags', '')
    
    # Load VIP senders if not provided
    if vip_senders is None:
        vip_senders = load_vip_senders()
    
    # Check for VIP senders FIRST (highest priority after urgent)
    for vip in vip_senders:
        if vip.lower() in sender:
            return ('IMPORTANT', f'⭐ VIP: {vip}')
    
    # Check for urgent keywords in subject
    for keyword in URGENT_KEYWORDS:
        if keyword in subject:
            return ('URGENT', f'keyword: {keyword}')
    
    # Check for urgent senders
    for pattern in URGENT_SENDERS:
        if pattern.lower() in sender:
            return ('URGENT', f'sender: {pattern}')
    
    # Check for important senders
    for pattern in IMPORTANT_SENDERS:
        if pattern.lower() in sender:
            return ('IMPORTANT', f'sender match')
    
    # Security/account related
    if any(kw in subject for kw in ['security', 'password', 'verification', 'login', 'ssh key']):
        return ('IMPORTANT', 'security-related')
    
    # Financial/billing
    if any(kw in subject for kw in ['invoice', 'billing', 'payment', 'receipt', 'statement']):
        return ('IMPORTANT', 'financial')
    
    # Check for newsletters
    for pattern in NEWSLETTER_SENDERS:
        if pattern.lower() in sender or pattern.lower() in subject:
            return ('INFO', 'newsletter')
    
    # Check for low priority
    for pattern in LOW_PRIORITY_SENDERS:
        if pattern.lower() in sender:
            return ('LOW', 'promotional/auto')
    
    # Default based on whether it's unread
    if '*' in flags:  # Unread marker
        return ('INFO', 'unread')
    
    return ('LOW', 'default')

def categorize_emails(emails: List[Dict]) -> Dict[str, List[Dict]]:
    """Categorize all emails into priority buckets."""
    categories = {
        'URGENT': [],
        'IMPORTANT': [],
        'INFO': [],
        'LOW': []
    }
    
    # Load VIP senders once for all emails
    vip_senders = load_vip_senders()
    
    for email in emails:
        category, reason = classify_email(email, vip_senders)
        email['_category'] = category
        email['_reason'] = reason
        categories[category].append(email)
    
    return categories


# =============================================================================
# VIP Management
# =============================================================================

def vip_add(email_pattern: str):
    """Add a VIP sender pattern."""
    senders = load_vip_senders()
    if email_pattern.lower() not in [s.lower() for s in senders]:
        senders.append(email_pattern)
        save_vip_senders(senders)
        print(f"✅ Added VIP: {email_pattern}")
    else:
        print(f"Already a VIP: {email_pattern}")

def vip_remove(email_pattern: str):
    """Remove a VIP sender pattern."""
    senders = load_vip_senders()
    lower_pattern = email_pattern.lower()
    new_senders = [s for s in senders if s.lower() != lower_pattern]
    if len(new_senders) < len(senders):
        save_vip_senders(new_senders)
        print(f"✅ Removed VIP: {email_pattern}")
    else:
        print(f"Not found: {email_pattern}")

def vip_list():
    """List all VIP senders."""
    senders = load_vip_senders()
    if senders:
        print(f"⭐ VIP Senders ({len(senders)}):\n")
        for s in sorted(senders):
            print(f"  • {s}")
    else:
        print("No VIP senders configured.")
        print("Add with: email-triage.py vip add 'person@email.com'")

# =============================================================================
# Digest Generation
# =============================================================================

def format_digest(categories: Dict[str, List[Dict]]) -> str:
    """Generate formatted digest for Telegram/console."""
    lines = ["📬 **Email Triage**\n"]
    
    # Urgent
    if categories['URGENT']:
        lines.append("🔴 **URGENT**")
        for e in categories['URGENT'][:5]:
            lines.append(f"  • {e.get('subject', '?')[:50]}")
            lines.append(f"    _{e.get('from', '?')[:30]}_")
        lines.append("")
    
    # Important
    if categories['IMPORTANT']:
        lines.append("🟠 **Important**")
        for e in categories['IMPORTANT'][:5]:
            lines.append(f"  • {e.get('subject', '?')[:50]}")
        lines.append("")
    
    # Info (just count)
    if categories['INFO']:
        lines.append(f"🔵 **Info/Newsletters:** {len(categories['INFO'])} emails")
    
    # Low (just count)
    if categories['LOW']:
        lines.append(f"⚪ **Low priority:** {len(categories['LOW'])} emails")
    
    # Summary stats
    total = sum(len(v) for v in categories.values())
    unread = sum(1 for cat in categories.values() for e in cat if '*' in e.get('flags', ''))
    lines.append(f"\n_Total: {total} | Unread: {unread}_")
    
    return '\n'.join(lines)

def format_json(categories: Dict[str, List[Dict]]) -> str:
    """Output as JSON for programmatic use."""
    summary = {
        'timestamp': datetime.now().isoformat(),
        'counts': {k: len(v) for k, v in categories.items()},
        'urgent': [{'subject': e.get('subject'), 'from': e.get('from')} 
                   for e in categories['URGENT']],
        'important': [{'subject': e.get('subject'), 'from': e.get('from')} 
                      for e in categories['IMPORTANT'][:10]],
    }
    return json.dumps(summary, indent=2)

# =============================================================================
# Main
# =============================================================================

def main():
    # Handle VIP subcommands first
    if len(sys.argv) >= 2 and sys.argv[1] == 'vip':
        if len(sys.argv) >= 3:
            action = sys.argv[2]
            if action == 'list':
                vip_list()
            elif action == 'add' and len(sys.argv) >= 4:
                vip_add(sys.argv[3])
            elif action == 'remove' and len(sys.argv) >= 4:
                vip_remove(sys.argv[3])
            else:
                print("Usage: email-triage.py vip [list|add|remove] [email]")
        else:
            vip_list()
        return
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Email triage tool')
    parser.add_argument('--unread', action='store_true', help='Unread only')
    parser.add_argument('--hours', type=int, default=24, help='Hours to scan')
    parser.add_argument('--count', type=int, default=30, help='Max emails to scan')
    parser.add_argument('--summary', action='store_true', help='Just show digest')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    # Fetch emails
    print("Scanning inbox...", file=sys.stderr)
    emails = list_emails(count=args.count)
    
    if not emails:
        print("No emails found or error fetching.")
        return
    
    # Filter by time if specified
    if args.hours < 24:
        cutoff = datetime.now() - timedelta(hours=args.hours)
        # Note: Would need to parse dates properly for real filtering
    
    # Categorize
    categories = categorize_emails(emails)
    
    # Show VIP count in output
    vip_count = sum(1 for e in categories['IMPORTANT'] if 'VIP' in e.get('_reason', ''))
    
    # Output
    if args.json:
        print(format_json(categories))
    else:
        print(format_digest(categories))
        if vip_count > 0:
            print(f"\n⭐ _Includes {vip_count} from VIP senders_")
    
    # Log the check
    log_path = Path.home() / '.openclaw/workspace/memory/email-checks.jsonl'
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'total': len(emails),
        'urgent': len(categories['URGENT']),
        'important': len(categories['IMPORTANT']),
        'vip': vip_count,
    }
    with open(log_path, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

if __name__ == '__main__':
    main()
