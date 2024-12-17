#!/bin/bash

# Function to check if CloudWatch agent is running
check_cloudwatch() {
    if ! pgrep -f amazon-cloudwatch-agent > /dev/null; then
        echo "AWS CloudWatch agent is not running. Starting it now..."
        sudo service amazon-cloudwatch-agent start
        if [ $? -eq 0 ]; then
            echo "AWS CloudWatch agent started successfully."
        else
            echo "Failed to start AWS CloudWatch agent."
        fi
    else
        echo "AWS CloudWatch agent is running."
    fi
}

# Ensure the script is added to crontab for execution on reboot
setup_cron() {
    sudo chmod +x ./cicd-scripts/helpers/check_cloudwatch.sh
    CRON_ENTRY="@reboot $(pwd)/cicd-scripts/helpers/check_cloudwatch.sh"

    # Update crontab, ensuring no duplicates
    (crontab -l 2>/dev/null | grep -v -F "check_cloudwatch.sh"; echo "$CRON_ENTRY") | crontab -
    echo "Crontab entry added to ensure the script runs on reboot."
}

# Execute the function
check_cloudwatch

# Add to crontab
setup_cron
