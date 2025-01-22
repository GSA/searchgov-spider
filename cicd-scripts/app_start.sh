#!/bin/bash -i

# CD into the current script directory (which != $pwd)
cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && cd ../

sudo chmod +x ./cicd-scripts/helpers/ensure_executable.sh
source ./cicd-scripts/helpers/ensure_executable.sh

# TODO: Make it part of the local env variable that is set by Ansible
SPIDER_RUN_WITH_UI=false

# Determine which script to run based on the SPIDER_RUN_WITH_UI flag
SCRIPT="./cicd-scripts/helpers/run_without_ui.sh"
if $SPIDER_RUN_WITH_UI; then
    SCRIPT="./cicd-scripts/helpers/run_with_ui.sh"
fi

# Ensure the script exists, is executable, and run it
ensure_executable "$SCRIPT"

echo "App start completed successfully."
