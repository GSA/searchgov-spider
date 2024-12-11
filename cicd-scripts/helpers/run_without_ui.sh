#!/bin/bash
SPIDER_PYTHON_VERSION=3.12
sudo bash -c "nohup /usr/local/bin/python${SPIDER_PYTHON_VERSION} ./search_gov_crawler/scrapy_scheduler.py > /var/log/scrapy.log 2>&1 &"
echo "Running no UI vesrion of searchgov-spider..."
