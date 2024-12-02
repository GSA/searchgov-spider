#!/bin/bash

# Function to check if CodeDeploy agent is running
check_codedeploy() {
    if ! pgrep -f codedeploy-agent > /dev/null; then
        echo "AWS CodeDeploy agent is not running. Starting it now..."
        sudo service codedeploy-agent start
        if [ $? -eq 0 ]; then
            echo "AWS CodeDeploy agent started successfully."
        else
            echo "Failed to start AWS CodeDeploy agent."
        fi
    else
        echo "AWS CodeDeploy agent is running."
    fi
}

# Ensure the script is added to crontab for execution on reboot
setup_cron() {
    sudo chmod +x ./cicd-scripts/helpers/check_codedeploy.sh
    CRON_ENTRY="@reboot /bin/bash $PWD/helpers/check_codedeploy.sh"

    # Update crontab, ensuring no duplicates
    (sudo crontab -l 2>/dev/null | grep -v -F "$CRON_ENTRY"; echo "$CRON_ENTRY") | sudo crontab -
    echo "Crontab entry added to ensure the script runs on reboot."
}

# Execute the function
check_codedeploy

# Add to crontab
setup_cron
