# Search_gov_spiders Info

* [Setup and Use](#setup-and-use)
    * [Option 1: command-line](#option-1-straight-from-command-line) 
    * [Option 2: server](#option-2-deploying-on-server-scrapyd)
* [Adding New Spiders](#adding-new-spiders)

## Setup and Use

### Option 1: straight from command-line
1. Navigate to the [*spiders*](./search_gov_spiders/spiders) directory
2. Enter one of two following commands:
ow t
    * This command will output the yielded URLs in the destination (relative to the [*spiders*](./search_gov_spiders/spiders) directory) and file format specified in the “FEEDS” variable of the [*settings.py*](./search_gov_spiders/settings.py) file:

            $ scrapy runspider <spider_file.py> 

    * This command will output the yielded URLs in the destination (relative to the [*spiders*](./search_gov_spiders/spiders) directory) and file format specified by the user:


            $ scrapy runspider <spider_file.py>  -o <filepath_to_output_folder/spider_output_filename.csv>             

### Option 2: deploying on server (Scrapyd)
1. First, install Scrapyd and scrapyd-client (library that helps eggify and deploy the Scrapy project to the Scrapyd server):
    
    *       $ pip install scrapyd
    *       $ pip install git+https://github.com/scrapy/scrapyd-client.git

2. Next, navigate to the [*scrapyd_files*](./scrapyd_files) directory and start the server :
    
        $ scrapyd 
    * Note: the directory where you start the server is arbitrary. It's simply where the logs and Scrapy project FEED destination (relative to the server directory) will be.

3. Navigate to the [*Scrapy project root directory*](./) and run this command to eggify the Scrapy project and deploy it to the Scrapyd server:
    
        $ scrapyd-deploy default


    * Note: This will simply deploy it to a local Scrapyd server. To add custom deployment endpoints, you navigate to the [*scrapy.cfg*](./scrapy.cfg) file and add or customize endpoints. 

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

1.  Navigate to anywhere within the [*Scrapy project root *](./) directory and run this command:

        $ scrapy genspider -t crawl <spider_name> "<spider_starting_domain>"

2. Open the */search_gov_spiders/search_gov_spiders/spiders/boilerplate.py* file and replace the lines of the generated spider with the lines of the boilerplate spider as dictated in the boilerplate file.

3. Modify the `rules` in the new spider as needed. Here's the [Scrapy rules documentation](https://docs.scrapy.org/en/latest/topics/spiders.html#crawling-rules) for the specifics.

4. To update the Scrapyd server with the new spider, run: 
        
        $ scrapyd-deploy <default or endpoint_name> 