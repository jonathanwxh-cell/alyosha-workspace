#!/usr/bin/env python3
"""
System Hygiene - Autonomous cleanup and maintenance
Runs monthly to prevent bloat from accumulated tracking/crons
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_DIR = WORKSPACE / "memory"
DATA_DIR = WORKSPACE / "data"
ARCHIVE_DIR = WORKSPACE / "archive"

def get_file_age_days(path):
    """Get file age in days from last modification"""
    try:
        mtime = os.path.getmtime(path)
        age = datetime.now() - datetime.fromtimestamp(mtime)
        return age.days
    except:
        return -1

def audit_tracking_files():
    """Find tracking files older than 90 days with no updates"""
    stale = []
    active = []
    
    patterns = ["*-tracker.csv", "*-log.jsonl", "*-tracking.json", "*-queue.json"]
    
    for pattern in patterns:
        for f in MEMORY_DIR.glob(pattern):
            age = get_file_age_days(f)
            size = f.stat().st_size if f.exists() else 0
            
            if age > 90:
                stale.append({"path": str(f.name), "age_days": age, "size_kb": size/1024})
            else:
                active.append({"path": str(f.name), "age_days": age, "size_kb": size/1024})
    
    # Also check data dir
    if DATA_DIR.exists():
        for f in DATA_DIR.glob("*.csv"):
            age = get_file_age_days(f)
            if age > 90:
                stale.append({"path": f"data/{f.name}", "age_days": age})
    
    return {"stale": stale, "active": active}

def audit_memory_files():
    """Check daily memory files, suggest archiving old months"""
    old_files = []
    cutoff = datetime.now() - timedelta(days=60)
    
    for f in MEMORY_DIR.glob("2*.md"):  # Daily files like 2026-01-15.md
        try:
            date_str = f.stem
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
            if file_date < cutoff:
                old_files.append(str(f.name))
        except:
            pass
    
    return old_files

def generate_report():
    """Generate hygiene audit report"""
    report = {
        "audit_date": datetime.now().isoformat(),
        "tracking_files": audit_tracking_files(),
        "old_daily_logs": audit_memory_files(),
        "recommendations": []
    }
    
    # Generate recommendations
    if report["tracking_files"]["stale"]:
        report["recommendations"].append(
            f"Archive {len(report['tracking_files']['stale'])} stale tracking files (>90 days)"
        )
    
    if len(report["old_daily_logs"]) > 30:
        report["recommendations"].append(
            f"Compress {len(report['old_daily_logs'])} old daily logs into monthly archives"
        )
    
    return report

def archive_stale_files(dry_run=True):
    """Move stale files to archive directory"""
    ARCHIVE_DIR.mkdir(exist_ok=True)
    month_dir = ARCHIVE_DIR / datetime.now().strftime("%Y-%m")
    
    audit = audit_tracking_files()
    archived = []
    
    for item in audit["stale"]:
        src = MEMORY_DIR / item["path"]
        if src.exists():
            if dry_run:
                archived.append(f"[DRY RUN] Would archive: {item['path']}")
            else:
                month_dir.mkdir(exist_ok=True)
                dest = month_dir / src.name
                src.rename(dest)
                archived.append(f"Archived: {item['path']} -> {dest}")
    
    return archived

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--archive":
        dry_run = "--dry-run" in sys.argv
        results = archive_stale_files(dry_run=dry_run)
        for r in results:
            print(r)
    else:
        report = generate_report()
        print(json.dumps(report, indent=2, default=str))
