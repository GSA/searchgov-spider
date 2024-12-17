#!/bin/bash

# Define the current directory
CURRENT_DIR=$(pwd)

# Define the .bashrc file location
BASHRC_FILE="$HOME/.bashrc"

# Check if .bashrc contains an export PYTHONPATH line
if grep -q "^export PYTHONPATH=" "$BASHRC_FILE"; then
    # Extract the existing PYTHONPATH line
    PYTHONPATH_LINE=$(grep "^export PYTHONPATH=" "$BASHRC_FILE")

    # Check if the current directory is already included
    if echo "$PYTHONPATH_LINE" | grep -q "$CURRENT_DIR"; then
        echo "PYTHONPATH already includes the current directory: $CURRENT_DIR"
    else
        # Ensure the updated line includes the starting and ending quotes
        CURRENT_PATHS=$(echo "$PYTHONPATH_LINE" | sed -e 's/^export PYTHONPATH=//' -e 's/^"//' -e 's/"$//')
        UPDATED_LINE="export PYTHONPATH=\"${CURRENT_PATHS}:${CURRENT_DIR}\""
        sed -i "s|^export PYTHONPATH=.*|$UPDATED_LINE|" "$BASHRC_FILE"
        echo "Updated PYTHONPATH to include the current directory: $CURRENT_DIR"
    fi
else
    # Add a new export PYTHONPATH line to .bashrc
    echo "export PYTHONPATH=\"\$PYTHONPATH:${CURRENT_DIR}\"" >> "$BASHRC_FILE"
    echo "Added new PYTHONPATH to .bashrc including the current directory: $CURRENT_DIR"
fi

# Apply changes for the current session
export PYTHONPATH=\"${CURRENT_PATHS//"\$PYTHONPATH"/}:${CURRENT_DIR}\"

echo "PYTHONPATH changes applied:"
echo $PYTHONPATH
