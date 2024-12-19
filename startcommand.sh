#!/bin/bash
echo "START START COMMAND"
# Define the current directory
# CURRENT_DIR=$(pwd)
# ls -a
# echo "Your current directory is $CURRENT_DIR"
cd search_gov_crawler
# ls
which python
echo $PYTHONPATH
python -c "print('Hello World')"
# python benchmark.py -f ./test_parallel_domain.json
python benchmark.py -d "quotes.toscrape.com" -u "https://quotes.toscrape.com"
# python -m http.server
echo "END START COMMAND"