#!/bin/bash
# Watchlist Intelligence Briefing Runner
# This script is meant to be called by the AI agent
# which will fetch news via web_search and pipe it through

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check for help flag
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    node "$SCRIPT_DIR/intel.js" --help
    exit 0
fi

# If news data is provided via stdin, pipe it through
if [ ! -t 0 ]; then
    node "$SCRIPT_DIR/intel.js" "$@"
else
    # Otherwise, output what queries are needed
    echo "No news data provided. Run with news JSON piped in:"
    echo ""
    echo "Example:"
    echo '  echo '"'"'{"NVDA": {"headlines": ["NVIDIA stock surges on AI demand"]}}'"'"' | ./run-briefing.sh'
    echo ""
    echo "Or use INTEL_MODE=queries to get required search queries:"
    INTEL_MODE=queries node "$SCRIPT_DIR/intel.js"
fi
