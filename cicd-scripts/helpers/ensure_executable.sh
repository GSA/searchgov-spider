#!/bin/bash

# Function to ensure a file exists, is executable, and then runs it
ensure_executable() {
  local script="$1"

  if [ -f "$script" ]; then
    chmod +x "$script"
    echo "$script is now executable."
    source "$script"
  else
    echo "Error: $script not found!"
    # exit 1
  fi
}
