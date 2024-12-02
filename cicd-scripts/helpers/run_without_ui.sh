#!/bin/bash

sudo bash -c 'nohup ./search_gov_crawler/scrapy_scheduler.py > /var/log/scrapy.log 2>&1 &'
