#!/bin/bash

echo "Stopping all scrapyd and scrapydweb tasks..."
# Kill all scrapydweb and scrapyd jobs
if sudo pkill -f "scrapydweb" 2>/dev/null; then
    echo "scrapydweb tasks stopped."
else
    echo "No scrapydweb tasks running."
fi

if sudo pkill -f "scrapyd" 2>/dev/null; then
    echo "scrapyd tasks stopped."
else
    echo "No scrapyd tasks running."
fi

# Display remaining scrapy processes (if any)
echo -e "\nRemaining scrapy processes (if any):"
ps -ef | grep scrapy | grep -v grep || echo "No scrapy processes running."

# Force kill any remaning scrapy background jobs still running
sudo ps aux | grep -ie [s]crapy | awk '{print $2}' | xargs kill -9
