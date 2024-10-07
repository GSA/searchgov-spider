#!/bin/bash

SCRAPYD_URL="http://127.0.0.1:6800/"
SCRAPYDWEB_URL="http://127.0.0.1:5000/"
SPIDER_URLS_API=https://staging.search.usa.gov/urls

# Function to check if a URL is up and running
function check_url() {
    local URL=$1
    local MAX_ATTEMPTS="${2:-3}"
    local DELAY=5
    local attempt=1

    while [ $attempt -le $MAX_ATTEMPTS ]; do
        if curl --output /dev/null --silent --head --fail "$URL"; then
            echo "Service at $URL is up on attempt $attempt."
            return 0
        else
            echo "Attempt $attempt: Service at $URL is not available, retrying in $DELAY seconds..."
        fi
        attempt=$((attempt+1))
        sleep $DELAY
    done

    echo "Service at $URL is still not available after $MAX_ATTEMPTS attempts."
    return 1
}

# Function to check if required command exists
function check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "Error: $1 is not installed or not in your PATH."
        exit 1
    fi
}

check_command "scrapyd"
check_command "scrapydweb"
check_command "curl"

echo "Killing any existing scrapyd and scrapydweb services"
sudo pkill -f "scrapydweb" 2>/dev/null
sudo pkill -f "scrapyd" 2>/dev/null

# Check search-gov /urls endpoint
echo "Checking search-gov /urls api..."
if check_url "$SPIDER_URLS_API"; then
    echo "The /urls api is up and running at endpoint: $SPIDER_URLS_API"
else
    echo "Error: /urls failed failed at endpoint: $SPIDER_URLS_API"
    exit 1
fi

echo "Running searchgov-spider application..."

# Start scrapyd
echo "Starting scrapyd service..."
sudo bash -c 'nohup scrapyd > /var/log/scrapyd.log 2>&1 &'
PID1=$!
echo "Started scrapyd with PID $PID1"

# Check if scrapyd is running
if check_url "$SCRAPYD_URL"; then
    echo "The scrapyd service is running at $SCRAPYD_URL"
    sudo bash -c 'nohup cd ./search_gov_crawler && scrapydweb > /var/log/scrapydweb.log 2>&1 &'
    PID2=$!
    echo "Started scrapydweb with PID $PID2"

    if check_url "$SCRAPYDWEB_URL"; then
        echo "The scrapydweb service is running at $SCRAPYDWEB_URL"
    else
        echo "Error: scrapydweb failed at $SCRAPYDWEB_URL."
        exit 1
    fi
else
    echo "Error: scrapyd failed at $SCRAPYD_URL."
    exit 1
fi

# Display the last few lines of logs
echo -e "\n-- Last 10 lines of scrapyd.log:\n"
tail -n 10 /var/log/scrapyd.log

echo -e "\n-- Last 10 lines of scrapydweb.log:\n"
tail -n 10 /var/log/scrapydweb.log
exit 0
