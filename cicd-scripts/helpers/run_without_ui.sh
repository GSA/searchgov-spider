#!/bin/bash

# Run the script in the background using the virtual environment
sudo chmod +x ./search_gov_crawler/scrapy_scheduler.py

sudo touch /var/log/scrapy_scheduler.log
sudo chown -R $(whoami) /var/log/scrapy_scheduler.log

nohup bash -c "source ./venv/bin/activate && ./venv/bin/python ./search_gov_crawler/scrapy_scheduler.py" | tee -a /var/log/scrapy_scheduler.log &

echo "Running no UI vesrion of searchgov-spider..."
