#!/bin/bash

# Define the current directory
CURRENT_DIR=$(pwd)

# Define the .bashrc file location
BASHRC_FILE="$HOME/.bashrc"

# Check if .bashrc contains an export PYTHONPATH line
if grep -q "^export PYTHONPATH=" "$BASHRC_FILE"; then
    # Extract the existing PYTHONPATH line
    PYTHONPATH_LINE=$(grep "^export PYTHONPATH=" "$BASHRC_FILE")

    # Construct the updated PYTHONPATH line
    UPDATED_LINE="export PYTHONPATH=\"$\PYTHONPATH:${CURRENT_DIR}\""

    # Update the .bashrc file
    sed -i "s|^export PYTHONPATH=.*|$UPDATED_LINE|" "$BASHRC_FILE"
    echo "Updated PYTHONPATH to include the current directory: $CURRENT_DIR"
else
    # Add a new export PYTHONPATH line to .bashrc
    echo "export PYTHONPATH=\"$\PYTHONPATH:${CURRENT_DIR}\"" >> "$BASHRC_FILE"
    echo "Added new PYTHONPATH to .bashrc including the current directory: $CURRENT_DIR"
fi

# Apply changes for the current session
export PYTHONPATH=":${CURRENT_DIR}"

echo "PYTHONPATH changes applied:"
echo $PYTHONPATH
