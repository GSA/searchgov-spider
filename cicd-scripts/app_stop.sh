#!/bin/bash

echo "Stopping all scrapy tasks..."

# Kill specific scrapy processes
pkill -f "scrapy crawl domain_spider"
pkill -f "scrapy crawl domain_spider_js"

# Display remaining scrapy processes (if any)
echo -e "\nRemaining scrapy processes (if any):"
ps -ef | grep scrapy | grep -v grep

# Check if there are any jobs still running (if started by this shell)
bg_jobs=$(jobs -p)

if [[ -n "$bg_jobs" ]]; then
    echo "Killing all background jobs..."
    # Kill all background jobs in this shell session
    jobs -p | xargs kill
else
    echo "No background jobs to kill."
fi

# List background jobs to confirm they are terminated
echo -e "\nBelow jobs list should be empty:"
jobs
