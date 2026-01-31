#!/bin/bash
#
# reddit-sg.sh - Fetch hot posts from r/singapore (or any subreddit)
#
# Usage:
#   ./reddit-sg.sh [subreddit] [limit] [--apify]
#
# Modes:
#   Default:  Uses web search to find Reddit posts (FREE, reliable)
#   --apify:  Uses Apify scraper (costs money, but gets full data)
#
# Examples:
#   ./reddit-sg.sh                    # r/singapore, 10 posts, free mode
#   ./reddit-sg.sh singapore 20       # r/singapore, 20 posts, free mode
#   ./reddit-sg.sh asksingapore 5     # r/asksingapore, 5 posts, free mode
#   ./reddit-sg.sh singapore 10 --apify  # Use Apify (costs $)
#

set -euo pipefail

SUBREDDIT="singapore"
LIMIT=10
USE_APIFY=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --apify)
      USE_APIFY=true
      shift
      ;;
    --help|-h)
      head -20 "$0" | tail -n +2 | sed 's/^# //' | sed 's/^#//'
      exit 0
      ;;
    *)
      if [[ -z "${SUBREDDIT_SET:-}" ]]; then
        SUBREDDIT="$1"
        SUBREDDIT_SET=1
      else
        LIMIT="$1"
      fi
      shift
      ;;
  esac
done

# ─────────────────────────────────────────────────────────────────
# FREE MODE: Use Brave Search API via OpenClaw
# This is called by the agent, not directly via curl
# ─────────────────────────────────────────────────────────────────
fetch_free() {
  echo "ℹ️  Using web search (free) - for full data, use --apify"
  echo ""
  echo "Search for: site:reddit.com/r/${SUBREDDIT}"
  echo ""
  echo "Note: This script cannot directly call the search API."
  echo "Instead, ask the agent to search for:"
  echo "  \"site:reddit.com/r/${SUBREDDIT} hot posts\""
  echo ""
  echo "Or use --apify flag for direct scraping (costs money)."
  exit 0
}

# ─────────────────────────────────────────────────────────────────
# APIFY MODE: Paid scraper (reliable, costs money)
# ─────────────────────────────────────────────────────────────────
fetch_apify() {
  # Check for Apify token
  local APIFY_TOKEN="${APIFY_TOKEN:-${APIFY_API_KEY:-}}"
  if [[ -z "$APIFY_TOKEN" ]]; then
    echo "Error: APIFY_TOKEN or APIFY_API_KEY not set" >&2
    echo "Set it with: export APIFY_TOKEN=your_token" >&2
    return 1
  fi
  
  echo "⚠️  Using Apify (this costs money). Consider asking the agent to search instead." >&2
  echo "" >&2
  
  curl -s "https://api.apify.com/v2/acts/trudax~reddit-scraper/run-sync-get-dataset-items?token=$APIFY_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"startUrls\": [{\"url\": \"https://www.reddit.com/r/$SUBREDDIT/hot/\"}],
      \"maxItems\": $LIMIT,
      \"proxy\": {\"useApifyProxy\": true}
    }" | jq -r '.[] | "[\(.score)] \(.title)\n  \(.url)\n"'
}

# ─────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────
echo "📍 r/$SUBREDDIT (top $LIMIT posts)"
echo ""

if [[ "$USE_APIFY" == true ]]; then
  fetch_apify
else
  fetch_free
fi
