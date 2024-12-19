#!/bin/bash
echo "BEGIN START COMMAND"
cd search_gov_crawler
python benchmark.py -f ./test_domains.json
echo "END START COMMAND"
