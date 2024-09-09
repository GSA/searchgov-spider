#!/bin/bash

echo "Killing all scrapy tasks"
pkill scrapy

# Kill all background jobs (by PID)
jobs -p | grep -o -E '\s\d+\s' | xargs kill

echo "\nBelow jobs list should be empty:"
jobs
