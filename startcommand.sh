#!/bin/bash
echo "BEGIN START COMMAND"
cd search_gov_crawler
python benchmark.py -f ../tests/search_gov_spiders/crawl-sites-test.json
echo "END START COMMAND"
