#!/usr/bin/env bash
#
# memory-compact.sh - Compress and archive old memories
#
# Usage:
#   ./memory-compact.sh [--dry-run] [--days N] [--force]
#
# What it does:
#   1. Summarizes daily logs older than N days into weekly summaries
#   2. Archives original daily files to memory/archive/
#   3. Compacts old reports/briefings into monthly digests
#   4. Prunes stale entries from tracking files
#

set -euo pipefail

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
MEMORY_DIR="$WORKSPACE/memory"
ARCHIVE_DIR="$MEMORY_DIR/archive"
REPORTS_DIR="$WORKSPACE/reports"
BRIEFINGS_DIR="$WORKSPACE/briefings"

DRY_RUN=false
DAYS_OLD=30  # Archive files older than this
FORCE=false

usage() {
  echo "Usage: $0 [OPTIONS]"
  echo ""
  echo "Options:"
  echo "  --dry-run    Show what would be done without doing it"
  echo "  --days N     Archive files older than N days (default: 30)"
  echo "  --force      Skip confirmation prompts"
  echo "  -h, --help   Show this help"
  exit 0
}

while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run) DRY_RUN=true; shift ;;
    --days) DAYS_OLD="$2"; shift 2 ;;
    --force) FORCE=true; shift ;;
    -h|--help) usage ;;
    *) echo "Unknown option: $1"; usage ;;
  esac
done

log() { echo "[memory-compact] $*"; }
dry() { [[ "$DRY_RUN" == true ]] && echo "[DRY-RUN] $*" || eval "$*"; }

# Calculate cutoff date
CUTOFF_DATE=$(date -d "$DAYS_OLD days ago" +%Y-%m-%d 2>/dev/null || date -v-${DAYS_OLD}d +%Y-%m-%d)
log "Archiving files older than: $CUTOFF_DATE"

# Ensure archive directory exists
mkdir -p "$ARCHIVE_DIR"
mkdir -p "$ARCHIVE_DIR/daily"
mkdir -p "$ARCHIVE_DIR/reports"
mkdir -p "$ARCHIVE_DIR/briefings"

# ─────────────────────────────────────────────────────────────────
# 1. Process old daily logs
# ─────────────────────────────────────────────────────────────────
log ""
log "=== Processing daily logs ==="

# Find daily files to archive
DAILY_FILES=()
for f in "$MEMORY_DIR"/????-??-??.md; do
  [[ -f "$f" ]] || continue
  filename=$(basename "$f" .md)
  if [[ "$filename" < "$CUTOFF_DATE" ]]; then
    DAILY_FILES+=("$f")
  fi
done

if [[ ${#DAILY_FILES[@]} -eq 0 ]]; then
  log "No daily logs older than $CUTOFF_DATE"
else
  log "Found ${#DAILY_FILES[@]} daily logs to archive"
  
  # Group by week for summarization
  declare -A WEEKS
  for f in "${DAILY_FILES[@]}"; do
    filename=$(basename "$f" .md)
    # Get ISO week number
    week=$(date -d "$filename" +%Y-W%V 2>/dev/null || date -j -f "%Y-%m-%d" "$filename" +%Y-W%V 2>/dev/null || echo "unknown")
    WEEKS[$week]+="$f "
  done
  
  # Create weekly summaries
  for week in "${!WEEKS[@]}"; do
    [[ "$week" == "unknown" ]] && continue
    
    summary_file="$ARCHIVE_DIR/weekly-$week.md"
    log "Creating weekly summary: $summary_file"
    
    if [[ "$DRY_RUN" != true ]]; then
      echo "# Weekly Summary: $week" > "$summary_file"
      echo "" >> "$summary_file"
      echo "Compiled from daily logs on $(date +%Y-%m-%d)" >> "$summary_file"
      echo "" >> "$summary_file"
      
      for f in ${WEEKS[$week]}; do
        filename=$(basename "$f" .md)
        echo "## $filename" >> "$summary_file"
        echo "" >> "$summary_file"
        # Extract key sections (headers and first few lines under each)
        grep -E "^#|^- |^\*\*|^[0-9]+\." "$f" 2>/dev/null | head -50 >> "$summary_file" || true
        echo "" >> "$summary_file"
      done
    fi
  done
  
  # Move original files to archive
  for f in "${DAILY_FILES[@]}"; do
    log "Archiving: $(basename "$f")"
    if [[ "$DRY_RUN" != true ]]; then
      mv "$f" "$ARCHIVE_DIR/daily/"
    fi
  done
fi

# ─────────────────────────────────────────────────────────────────
# 2. Archive old reports
# ─────────────────────────────────────────────────────────────────
log ""
log "=== Processing reports ==="

if [[ -d "$REPORTS_DIR" ]]; then
  OLD_REPORTS=$(find "$REPORTS_DIR" -maxdepth 1 -name "*.md" -type f -mtime +$DAYS_OLD 2>/dev/null | wc -l)
  log "Found $OLD_REPORTS reports older than $DAYS_OLD days"
  
  if [[ $OLD_REPORTS -gt 0 && "$DRY_RUN" != true ]]; then
    find "$REPORTS_DIR" -maxdepth 1 -name "*.md" -type f -mtime +$DAYS_OLD -exec mv {} "$ARCHIVE_DIR/reports/" \;
    log "Archived $OLD_REPORTS reports"
  fi
else
  log "No reports directory"
fi

# ─────────────────────────────────────────────────────────────────
# 3. Archive old briefings
# ─────────────────────────────────────────────────────────────────
log ""
log "=== Processing briefings ==="

if [[ -d "$BRIEFINGS_DIR" ]]; then
  OLD_BRIEFINGS=$(find "$BRIEFINGS_DIR" -maxdepth 1 -name "*.md" -type f -mtime +$DAYS_OLD 2>/dev/null | wc -l)
  log "Found $OLD_BRIEFINGS briefings older than $DAYS_OLD days"
  
  if [[ $OLD_BRIEFINGS -gt 0 && "$DRY_RUN" != true ]]; then
    find "$BRIEFINGS_DIR" -maxdepth 1 -name "*.md" -type f -mtime +$DAYS_OLD -exec mv {} "$ARCHIVE_DIR/briefings/" \;
    log "Archived $OLD_BRIEFINGS briefings"
  fi
else
  log "No briefings directory"
fi

# ─────────────────────────────────────────────────────────────────
# 4. Prune stale tracking data
# ─────────────────────────────────────────────────────────────────
log ""
log "=== Pruning tracking files ==="

# Clean old entries from reflections.jsonl (keep last 100)
REFLECTIONS="$MEMORY_DIR/reflections.jsonl"
if [[ -f "$REFLECTIONS" ]]; then
  lines=$(wc -l < "$REFLECTIONS")
  if [[ $lines -gt 100 ]]; then
    log "Trimming reflections.jsonl from $lines to 100 entries"
    if [[ "$DRY_RUN" != true ]]; then
      tail -100 "$REFLECTIONS" > "$REFLECTIONS.tmp" && mv "$REFLECTIONS.tmp" "$REFLECTIONS"
    fi
  else
    log "reflections.jsonl has $lines entries (under limit)"
  fi
fi

# Clean old entries from synthesis-queue.json
SYNTHESIS="$MEMORY_DIR/synthesis-queue.json"
if [[ -f "$SYNTHESIS" ]]; then
  # Just note it exists - manual review needed for JSON
  log "synthesis-queue.json exists - review manually for stale items"
fi

# ─────────────────────────────────────────────────────────────────
# 5. Report
# ─────────────────────────────────────────────────────────────────
log ""
log "=== Summary ==="
log "Archive location: $ARCHIVE_DIR"

if [[ "$DRY_RUN" == true ]]; then
  log ""
  log "This was a dry run. No files were modified."
  log "Run without --dry-run to apply changes."
fi

# Show archive stats
if [[ -d "$ARCHIVE_DIR" ]]; then
  log ""
  log "Archive contents:"
  log "  Daily logs: $(ls -1 "$ARCHIVE_DIR/daily" 2>/dev/null | wc -l) files"
  log "  Weekly summaries: $(ls -1 "$ARCHIVE_DIR"/weekly-*.md 2>/dev/null | wc -l) files"
  log "  Reports: $(ls -1 "$ARCHIVE_DIR/reports" 2>/dev/null | wc -l) files"
  log "  Briefings: $(ls -1 "$ARCHIVE_DIR/briefings" 2>/dev/null | wc -l) files"
fi

log ""
log "✅ Memory compaction complete"
