#!/bin/bash
# Quick FMP quote lookup
# Usage: ./fmp-quote.sh NVDA AAPL MSFT

source ~/.openclaw/workspace/.secure/fmp.env

for symbol in "$@"; do
  data=$(curl -s "https://financialmodelingprep.com/stable/quote?symbol=$symbol&apikey=$FMP_API_KEY")
  echo "$data" | jq -r '.[] | "\(.symbol) (\(.name)): $\(.price) | Change: \(.change) (\(.changePercentage | . * 100 | round / 100)%) | MCap: $\(.marketCap / 1e9 | . * 10 | round / 10)B | 52W: $\(.yearLow)-$\(.yearHigh)"'
done
