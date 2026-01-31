#!/bin/bash
# Reddit Singapore scraper using Apify
# Usage: ./reddit-sg.sh [subreddit] [limit]

SUBREDDIT="${1:-singapore}"
LIMIT="${2:-10}"

# Check for Apify token (supports both env var names)
APIFY_TOKEN="${APIFY_TOKEN:-$APIFY_API_KEY}"
if [ -z "$APIFY_TOKEN" ]; then
  echo "Error: APIFY_TOKEN or APIFY_API_KEY not set"
  exit 1
fi

# Run the Reddit scraper actor
curl -s "https://api.apify.com/v2/acts/trudax~reddit-scraper/run-sync-get-dataset-items?token=$APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"startUrls\": [{\"url\": \"https://www.reddit.com/r/$SUBREDDIT/hot/\"}],
    \"maxItems\": $LIMIT,
    \"proxy\": {\"useApifyProxy\": true}
  }" | jq -r '.[] | "[\(.score)] \(.title)\n  \(.url)\n"'
