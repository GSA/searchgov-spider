#!/bin/bash

LOG_FILE=/var/log/scrapy_scheduler.log
START_SCRIPT=search_gov_crawler/scrapy_scheduler.py

source ~/.profile

# Run the script in the background using the virtual environment
sudo chmod +x ./$START_SCRIPT

sudo touch $LOG_FILE
sudo chown -R $(whoami) $LOG_FILE

echo PYTHONPATH is $PYTHONPATH

nohup bash -c "source ./venv/bin/activate && ./venv/bin/python ./$START_SCRIPT" >> $LOG_FILE 2>&1 &

echo "Running no UI vesrion of searchgov-spider..."
