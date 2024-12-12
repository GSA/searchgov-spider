#!/bin/bash

# PUBLIC
SPIDER_RUN_WITH_UI=false

if $SPIDER_RUN_WITH_UI ; then
    sudo chmod +x ./cicd-scripts/helpers/run_with_ui.sh
    source ./cicd-scripts/helpers/run_with_ui.sh
else
    sudo chmod +x ./cicd-scripts/helpers/run_without_ui.sh
    source ./cicd-scripts/helpers/run_without_ui.sh
fi
