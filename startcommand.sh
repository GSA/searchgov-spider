#!/bin/bash
cd search_gov_crawler
bash -c "scrapy crawl domain_spider -a allowed_domains="quotes.toscrape.com/tag/" -a start_urls="https://quotes.toscrape.com""