#!/bin/bash
# Quick scheduling check for heartbeats
# Usage: ./schedule-check.sh [category]

CATEGORY="${1:-}"

if [ -n "$CATEGORY" ]; then
    python3 ~/scripts/scheduling-advisor.py should-surface --category "$CATEGORY"
else
    python3 ~/scripts/scheduling-advisor.py should-surface
fi
