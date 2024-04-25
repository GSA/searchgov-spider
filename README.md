# search-gov-indexing
Indexing ingest and processing for Search.gov


## Indexing Module List


### Alphanumeric Search Model 
Uses currently indexed data in ElasticSearch to generate a model for improving alphanumeric search within Search.gov

| Module | Description|
| -------- | ------|
| Data Grabber |Loads data from a snapshot into ElasticSearch for analysis.|
| RegEx Crawler |Using RegEx patterns will crawl ElasticSearch looking for alphanumeric Strings|

### Scrapy Web Crawler
The spider can either scrape for URLs from the list of required domains or take in a domain and starting URL to scrape 
site/domain.

## Running Against All Listed Search.gov Domains
Navigate down to `search-gov-indexing/spider-foundational-work/search_gov_spiders/search_gov_spiders/spiders/`, then
enter the command below:
```commandline
scrapy crawl domain_spider
```
^^^ This will take a _long_ time
### Running Against A Specific Domain
In the same directory specified above, enter the command below, adding the domain and starting URL for the crawler:
```commandline
scrapy crawl domain_spider -a domain=example.com -a urls=www.example.com
```
