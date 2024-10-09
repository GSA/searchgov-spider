# Scrapy settings for search_gov_spiders project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

# Settings for json logging
LOG_ENABLED = False
JSON_LOGGING_ENABLED = True

BOT_NAME = "search_gov_spiders"

SPIDER_MODULES = ["search_gov_spiders.spiders"]
NEWSPIDER_MODULE = "search_gov_spiders.spiders"

# Crawl responsibly by identifying yourself
# (and your website) on the user-agent
USER_AGENT = "usasearch"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

LOG_LEVEL = "INFO"

# settings for broad crawling
SCHEDULER_PRIORITY_QUEUE = "scrapy.pqueues.DownloaderAwarePriorityQueue"
# Configure maximum concurrent requests performed by Scrapy (default: 16)
# For optimum performance, you should pick a concurrency where
# CPU usage is at 80-90%.
CONCURRENT_REQUESTS = 100
CONCURRENT_REQUESTS_PER_DOMAIN = 100
COOKIES_ENABLED = False
REACTOR_THREADPOOL_MAXSIZE = 20
RETRY_ENABLED = False
DOWNLOAD_TIMEOUT = 15
# set to True for BFO
AJAXCRAWL_ENABLED = True
# crawl in BFO order rather than DFO
DEPTH_PRIORITY = 1
SCHEDULER_DISK_QUEUE = "scrapy.squeues.PickleFifoDiskQueue"
SCHEDULER_MEMORY_QUEUE = "scrapy.squeues.FifoMemoryQueue"


# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0
# The download delay setting will honor only one of:


# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    "search_gov_spiders.middlewares.SearchGovSpidersSpiderMiddleware": 543,
}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    "search_gov_spiders.middlewares.SearchGovSpidersOffsiteMiddleware": 100,
    "search_gov_spiders.middlewares.SearchGovSpidersDownloaderMiddleware": 543,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
    "search_gov_spiders.extensions.json_logging.JsonLogging": -1,
    "scrapy.extensions.closespider.CloseSpider": 500,
}

CLOSESPIDER_TIMEOUT_NO_ITEM = 50

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "search_gov_spiders.pipelines.DeDeuplicatorPipeline": 100,
    "search_gov_spiders.pipelines.SearchGovSpidersPipeline": 200,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = False
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 5

# Enable and configure HTTP caching (disabled by default)
# HTTPCACHE_ENABLED must be set to false for scrapy playwright to run
HTTPCACHE_ENABLED = False
HTTPCACHE_DIR = "httpcache"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

FEEDS = {
    "scrapy_urls/%(name)s/%(name)s_%(time)s.txt": {
        "format": "csv",
    }
}

# Playwright Settings
PLAYWRIGHT_BROWSER_TYPE = "chromium"

PLAYWRIGHT_LAUNCH_OPTIONS = {"headless": True}

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
