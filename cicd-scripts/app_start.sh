#!/bin/bash

echo "Running searchgov-spider application..."

# Kill existing scrapy processes started by this script
pkill -f "scrapy crawl domain_spider"
pkill -f "scrapy crawl domain_spider_js"

# Start the scrapy crawlers and redirect their outputs to separate files
nohup scrapy crawl domain_spider > domain_spider.log 2>&1 &
PID1=$!
echo "Started domain_spider with PID $PID1"

nohup scrapy crawl domain_spider_js > domain_spider_js.log 2>&1 &
PID2=$!
echo "Started domain_spider_js with PID $PID2"

# Display currently running scrapy processes
echo -e "\nCurrent running scrapy processes:"
ps -ef | grep scrapy | grep -v grep

# Display the last few lines of the logs
echo -e "\nLast few lines of domain_spider.log:"
tail -n 10 domain_spider.log

echo -e "\nLast few lines of domain_spider_js.log:"
tail -n 10 domain_spider_js.log
