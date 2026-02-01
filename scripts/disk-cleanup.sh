#!/bin/bash
# Disk cleanup script for OpenClaw
# Runs weekly to keep disk usage in check

set -e

OPENCLAW_DIR="/home/ubuntu/.openclaw"
WORKSPACE_DIR="$OPENCLAW_DIR/workspace"
LOG_FILE="$WORKSPACE_DIR/memory/cleanup-log.jsonl"

# Function to log cleanup entry
log_cleanup() {
    local freed=$1
    local avail=$2
    echo "{\"timestamp\":\"$(date -Iseconds)\",\"freedKB\":$freed,\"availableKB\":$avail}" >> "$LOG_FILE"
}

echo "=== OpenClaw Disk Cleanup ==="
echo "Started: $(date)"

# Track space before
BEFORE=$(df / --output=avail | tail -1 | tr -d ' ')

# 1. Browser cache older than 7 days
echo "Cleaning browser cache..."
find "$OPENCLAW_DIR/browser" -type f -mtime +7 -delete 2>/dev/null || true
find "$OPENCLAW_DIR/browser" -type d -empty -delete 2>/dev/null || true

# 2. Session transcripts older than 14 days
echo "Cleaning old session transcripts..."
find "$OPENCLAW_DIR/agents" -name "*.jsonl" -mtime +14 -delete 2>/dev/null || true

# 3. Inbound media older than 30 days
echo "Cleaning old inbound media..."
find "$OPENCLAW_DIR/media/inbound" -type f -mtime +30 -delete 2>/dev/null || true

# 4. Browser screenshots older than 7 days
echo "Cleaning old browser screenshots..."
find "$OPENCLAW_DIR/media/browser" -type f -mtime +7 -delete 2>/dev/null || true

# 5. NPM logs and cache
echo "Cleaning npm logs..."
rm -rf /home/ubuntu/.npm/_logs/* 2>/dev/null || true

# 6. Temp files
echo "Cleaning temp files..."
rm -rf /tmp/puppeteer* /tmp/chromium* /tmp/genart-* 2>/dev/null || true

# 7. Old market briefs (keep last 7 days)
echo "Cleaning old market briefs..."
find "$WORKSPACE_DIR/memory/market-briefs" -type f -mtime +7 -delete 2>/dev/null || true

# 8. Python cache (NEW)
echo "Cleaning Python cache..."
find "$WORKSPACE_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$WORKSPACE_DIR" -name "*.pyc" -delete 2>/dev/null || true
find /home/ubuntu -maxdepth 3 -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# 9. Pip cache older than 30 days (NEW)
echo "Cleaning pip cache..."
pip cache purge 2>/dev/null || true

# 10. Cargo registry cache older than 30 days (NEW - for himalaya etc)
echo "Cleaning cargo cache..."
if [ -d "/home/ubuntu/.cargo/registry/cache" ]; then
    find /home/ubuntu/.cargo/registry/cache -type f -mtime +30 -delete 2>/dev/null || true
fi

# 11. Old reports (keep last 14 days) (NEW)
echo "Cleaning old reports..."
find "$WORKSPACE_DIR/reports" -name "*.md" -mtime +14 -delete 2>/dev/null || true

# 12. Journal logs older than 7 days (NEW)
echo "Cleaning old journal logs..."
sudo journalctl --vacuum-time=7d 2>/dev/null || true

# Track space after
AFTER=$(df / --output=avail | tail -1 | tr -d ' ')
FREED=$((AFTER - BEFORE))

echo "=== Cleanup Complete ==="
echo "Space freed: ${FREED}K"
echo "Available now: $(df -h / --output=avail | tail -1)"
echo "Finished: $(date)"

# Log result for tracking
log_cleanup "$FREED" "$AFTER"
