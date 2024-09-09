#!/bin/bash

echo "Activating virtual environment..."
source /home/ec2-user/app/venv/bin/activate

echo "Running searchgov-spider application..."
# python /home/ec2-user/app/app.py

pkill scrapy


nohup scrapy crawl domain_spider &
nohup scrapy crawl domain_spider_js &

echo "\nCurrent running crawl jobs:"
jobs

echo "\noutput:"
cat nohup.out
