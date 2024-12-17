#!/bin/bash

# Run the script in the background using the virtual environment
chmod +x ./search_gov_crawler/scrapy_scheduler.py

sudo nohup bash -c "source ./venv/bin/activate && ./venv/bin/python ./search_gov_crawler/scrapy_scheduler.py" > /var/log/scrapy_scheduler.log 2>&1 &

echo "Running no UI vesrion of searchgov-spider..."
