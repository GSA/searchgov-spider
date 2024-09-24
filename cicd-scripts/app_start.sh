#!/bin/bash

SCRAPYD_URL="http://127.0.0.1:6800/"
SCRAPYDWEB_URL="http://127.0.0.1:5000/"
CICD_SCRIPTS_BASE_DIR=$(pwd)

# Function to check if a URL is up and running
function check_url() {
    local URL=$1
    local MAX_ATTEMPTS=3
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

# Function to combine current directory with subdirectory and return absolute path
function get_abs_path() {
    local base_dir="$CICD_SCRIPTS_BASE_DIR"
    local sub_dir="$1"

    if [[ "$sub_dir" == /* ]]; then
        echo "$sub_dir"
    else
        echo "$base_dir/$sub_dir"
    fi
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

scrapyd_dir=$(get_abs_path "../")
scrapydweb_dir=$(get_abs_path "../search_gov_crawler")

echo "Killing any existing scrapyd and scrapydweb services"
sudo pkill -f "scrapydweb" 2>/dev/null
sudo pkill -f "scrapyd" 2>/dev/null

echo "Running searchgov-spider application..."

# Start scrapyd
echo "Starting scrapyd service..."
cd "$scrapyd_dir"
sudo nohup scrapyd > /var/log/scrapyd.log 2>&1 &
PID1=$!
echo "Started scrapyd with PID $PID1"

# Check if scrapyd is running
if check_url "$SCRAPYD_URL"; then
    echo "The scrapyd service is running at $SCRAPYD_URL"
    cd "$scrapydweb_dir"
    sudo nohup scrapydweb > /var/log/scrapydweb.log 2>&1 &
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

# Add startup cron for this script:
echo "
export LATEST_SPIDER_CICD_DEPLOY_PATH=$(CICD_SCRIPTS_BASE_DIR)
" | tee '/etc/profile.d/spider_env.sh' > /dev/null

# Display the last few lines of logs
echo -e "\n-- Last 10 lines of scrapyd.log:\n"
tail -n 10 /var/log/scrapyd.log

echo -e "\n-- Last 10 lines of scrapydweb.log:\n"
tail -n 10 /var/log/scrapydweb.log
exit 0
