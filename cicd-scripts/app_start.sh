#!/bin/bash

echo "Running searchgov-spider application..."

pkill scrapy

nohup scrapy crawl domain_spider &
nohup scrapy crawl domain_spider_js &

echo "\nCurrent running crawl jobs:"
jobs

echo "\noutput:"
cat nohup.out
