#!/bin/bash
# Scrape r/singapore hot posts via Apify
# Usage: ./reddit-sg.sh [max_items]

MAX_ITEMS=${1:-20}
TOKEN=$(grep APIFY_API_KEY ~/.openclaw/.env | cut -d'=' -f2)

# Start the run
RUN_RESPONSE=$(curl -s -X POST "https://api.apify.com/v2/acts/trudax~reddit-scraper-lite/runs?token=$TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"startUrls\": [{\"url\": \"https://www.reddit.com/r/singapore/hot/\"}],
    \"maxItems\": $MAX_ITEMS,
    \"sort\": \"hot\",
    \"includeComments\": false
  }")

RUN_ID=$(echo $RUN_RESPONSE | jq -r '.data.id')
DATASET_ID=$(echo $RUN_RESPONSE | jq -r '.data.defaultDatasetId')

echo "Started run $RUN_ID, waiting..."

# Poll until done
while true; do
  STATUS=$(curl -s "https://api.apify.com/v2/actor-runs/$RUN_ID?token=$TOKEN" | jq -r '.data.status')
  if [ "$STATUS" = "SUCCEEDED" ] || [ "$STATUS" = "FAILED" ]; then
    break
  fi
  sleep 5
done

if [ "$STATUS" = "SUCCEEDED" ]; then
  echo "=== r/singapore Hot Posts ==="
  curl -s "https://api.apify.com/v2/datasets/$DATASET_ID/items?token=$TOKEN&limit=50" | \
    jq -r '[.[] | select(.dataType == "post")] | sort_by(-.upVotes) | .[:15] | .[] | "⬆️ \(.upVotes) | \(.title) [\(.numberOfComments) comments]\n   \(.url)\n"'
else
  echo "Run failed: $STATUS"
fi
