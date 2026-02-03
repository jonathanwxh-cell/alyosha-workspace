#!/bin/bash
# Auto-commit script for workspace
# Run via cron daily

cd /home/ubuntu/.openclaw/workspace

# Check if there are changes
if [[ -z $(git status --porcelain) ]]; then
    echo "No changes to commit"
    exit 0
fi

# Stage all changes (except .secure and other sensitive paths)
git add -A
git reset -- .secure/ 2>/dev/null || true

# Generate commit message based on changed files
CHANGED=$(git diff --cached --name-only | head -20)
SCRIPTS=$(echo "$CHANGED" | grep "^scripts/" | wc -l)
MEMORY=$(echo "$CHANGED" | grep "^memory/" | wc -l)
DOCS=$(echo "$CHANGED" | grep "^docs/" | wc -l)

MSG="Auto-commit $(date +%Y-%m-%d)"
[[ $SCRIPTS -gt 0 ]] && MSG="$MSG | $SCRIPTS scripts"
[[ $MEMORY -gt 0 ]] && MSG="$MSG | $MEMORY memory files"
[[ $DOCS -gt 0 ]] && MSG="$MSG | $DOCS docs"

# Commit and push
git commit -m "$MSG"
git push origin master

echo "Committed and pushed: $MSG"
