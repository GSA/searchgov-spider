#!/bin/bash

echo "Stopping all scrapyd and scrapydweb tasks..."
# pkill for scrapydweb and scrapyd
if pkill -f "scrapydweb" 2>/dev/null; then
    echo "scrapydweb tasks stopped."
else
    echo "No scrapydweb tasks running."
fi

if pkill -f "scrapyd" 2>/dev/null; then
    echo "scrapyd tasks stopped."
else
    echo "No scrapyd tasks running."
fi

# Display remaining scrapy processes (if any)
echo -e "\nRemaining scrapy processes (if any):"
ps -ef | grep scrapy | grep -v grep || echo "No scrapy processes running."

# Check for any background jobs still running
bg_jobs=$(jobs -p)

if [[ -n "$bg_jobs" ]]; then
    echo "Killing all background jobs..."
    # Kill all background jobs in this shell session
    jobs -p | xargs -r kill
else
    echo "No background jobs to kill."
fi

# List background jobs to confirm they are terminated
echo -e "\nBelow jobs list should be empty:"
jobs
