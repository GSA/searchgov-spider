#!/bin/bash

# PUBLIC
RUN_WITH_UI=true

if $RUN_WITH_UI ; then
    source ./cicd-scripts/helpers/run_with_ui.sh
else
    source ./cicd-scripts/helpers/run_without_ui.sh
fi
