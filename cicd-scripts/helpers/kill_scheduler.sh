#!/bin/bash

# Find the process ID of the running scrapy_scheduler.py script
echo "Searching for scrapy_scheduler.py process..."
PROCESS_ID=$(pgrep -f "scrapy_scheduler.py")

# Check if the process exists
if [ -z "$PROCESS_ID" ]; then
  echo "No running process found for scrapy_scheduler.py."
  exit 0
fi

# Kill the process
echo "Killing process with PID: $PROCESS_ID"
kill "$PROCESS_ID"

sleep 3

# Verify if the process was killed
if [ $? -eq 0 ]; then
  echo "Process scrapy_scheduler.py (PID: $PROCESS_ID) has been terminated."
else
  echo "Failed to terminate the process. Please check manually."
  exit 1
fi
