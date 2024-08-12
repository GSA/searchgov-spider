# search-spider
The home for the spider that supports search.gov.

#### Table of contents:
* [About](#about)
  * [Core Scrapy File Strcture](#core-scrapy-file-structure)
  * [Scrapy Web Crawler](#scrapy-web-crawler)
* [Quick Start](#quick-start)
  * [Running Against All Listed Search.gov Domains](#running-against-all-listed-searchgov-domains)
  * [Running Against A Specific Domain](#running-against-a-specific-domain)
* [Setup and Use](#setup-and-use)
  * [Option 1: command-line](#option-1-straight-from-command-line)
  * [Option 2: server](#option-2-deploying-on-server-scrapyd)
* [Adding New Spiders](#adding-new-spiders)


## About
The spider uses the open source [scrapy](https://scrapy.org/) framework.

The spider can be found at `search_gov_crawler/search_gov_spiders/spiders/domain_spider.py`.

### Core Scrapy File Structure
*Note: Other files and directories are within the repository but the folders and files below relate to those needed for the scrapy framework.

```bash
├── search_gov_crawler ( scrapy root )
│   ├── search_gov_spider ( scrapy project *Note multiple projects can exist within a project root )
│   │   ├── spiders
│   │   │   ├── domain_spider.py ( main spider )
│   │   ├── utility_files ( includes text files with domains to scrape )
│   │   ├── items.py
│   │   ├── middlewares.py
│   │   ├── pipelines.py
│   │   ├── settings.py
│   ├── scrapy.cfg
```

### Scrapy Web Crawler
The spider can either scrape for URLs from the list of required domains or take in a domain and starting URL to scrape a site/domain.

Running the spider produces a list of urls found in `search_gov_crawler/search_gov_spiders/spiders/scrapy_urls/{spider_name}/{spider_name}_{date}-{UTC_time}.txt`.

## Quick Start
Make sure to run `pip install -r requirements.txt` and `playwright install` before running any spiders.

### Running Against All Listed Search.gov Domains
Navigate down to `search_gov_crawler/search_gov_spiders/spiders/`, then
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

## Setup and Use
Make sure to run `pip install -r requirements.txt` and `playwright install` before running any spiders.

### Option 1: straight from command-line
1. Navigate to the [*spiders*](search_gov_crawler/search_gov_spiders/spiders) directory
2. Enter one of two following commands:

    * This command will output the yielded URLs in the destination (relative to the [*spiders*](search_gov_crawler/search_gov_spiders/spiders) directory) and file format specified in the “FEEDS” variable of the [*settings.py*](search_gov_crawler/search_gov_spiders/settings.py) file:

          $ scrapy runspider <spider_file.py>

    * This command will output the yielded URLs in the destination (relative to the [*spiders*](search_gov_crawler/search_gov_spiders/spiders) directory) and file format specified by the user:


          $ scrapy runspider <spider_file.py>  -o <filepath_to_output_folder/spider_output_filename.csv>

### Option 2: deploying on server (Scrapyd)
1. First, install Scrapyd and scrapyd-client (library that helps eggify and deploy the Scrapy project to the Scrapyd server):

    *       $ pip install scrapyd
    *       $ pip install git+https://github.com/scrapy/scrapyd-client.git

2. Next, navigate to the [*scrapyd_files*](search_gov_crawler/scrapyd_files) directory and start the server :

        $ scrapyd
    * Note: the directory where you start the server is arbitrary. It's simply where the logs and Scrapy project FEED destination (relative to the server directory) will be.

3. Navigate to the [*Scrapy project root directory*](search_gov_crawler) and run this command to eggify the Scrapy project and deploy it to the Scrapyd server:

        $ scrapyd-deploy default


    * Note: This will simply deploy it to a local Scrapyd server. To add custom deployment endpoints, you navigate to the [*scrapy.cfg*](search_gov_crawler/scrapy.cfg) file and add or customize endpoints.

        For instance, if you wanted local and production endpoints:

            [settings]
            default = search_gov_spiders.settings

            [deploy: local]
            url = http://localhost:6800/
            project = search_gov_spiders

            [deploy: production]
            url = <IP_ADDRESS>
            project = search_gov_spiders

        To deploy:

            # deploy locally
            scrapyd-deploy local

            # deploy production
            scrapyd-deploy production

4. For an interface to view jobs (pending, running, finished) and logs, access http://localhost:6800/. However, to actually manipulate the spiders deployed to the Scrapyd server, you'll need to use the [Scrapyd JSON API](https://scrapyd.readthedocs.io/en/latest/api.html).

    Some most-used commands:

    * Schedule a job:

            $ curl http://localhost:6800/schedule.json -d project=search_gov_spiders -d spider=<spider_name>
    * Check load status of a service:

            $ curl http://localhost:6800/daemonstatus.json

## Adding new spiders

1.  Navigate to anywhere within the [*Scrapy project root *](search_gov_crawler) directory and run this command:

        $ scrapy genspider -t crawl <spider_name> "<spider_starting_domain>"

2. Open the `/search_gov_spiders/search_gov_spiders/spiders/boilerplate.py` file and replace the lines of the generated spider with the lines of the boilerplate spider as dictated in the boilerplate file.

3. Modify the `rules` in the new spider as needed. Here's the [Scrapy rules documentation](https://docs.scrapy.org/en/latest/topics/spiders.html#crawling-rules) for the specifics.

4. To update the Scrapyd server with the new spider, run:

        $ scrapyd-deploy <default or endpoint_name>

        ## Running Against All Listed Search.gov Domains
