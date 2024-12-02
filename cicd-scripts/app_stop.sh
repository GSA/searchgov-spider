#!/bin/bash

# Clear all cache
echo "Purge all pip cache..."
sudo pip cache purge

# Kill scrapy schedular (if running):
echo "Stopping scrapy_scheduler.py (if running)"
sudo chmod +x ./cicd-scripts/helpers/kill_scheduler.sh
source ./cicd-scripts/helpers/kill_scheduler.sh

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

# Kill all nohup jobs (runs with python)
ps -ef | grep nohup | grep -v grep | awk '{print $2}'

# Remove other deploy cron jobs:
#!/bin/bash

# Function to remove crontab entries referencing a given cron entry string
remove_cron_entry() {
    if [ -z "$1" ]; then
        echo "Error: No cron entry provided."
        exit 1
    fi

    CRON_ENTRY="$1"

    # Remove entries referencing the script
    sudo crontab -l 2>/dev/null | grep -v -F "$CRON_ENTRY" | sudo crontab -

    echo "Removed any crontab entries referencing $CRON_ENTRY."
}

# Remove any other cron job entries
remove_cron_entry "check_cloudwatch.sh"
remove_cron_entry "check_codedeploy.sh"
