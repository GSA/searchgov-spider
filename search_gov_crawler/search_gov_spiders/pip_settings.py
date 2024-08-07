# Scrapy settings for search_gov_spiders project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "search_gov_spiders"

SPIDER_MODULES = ["search_gov_crawler.search_gov_spiders.spiders"]

NEWSPIDER_MODULE = "search_gov_crawler.search_gov_spiders.spiders"

USER_AGENT = "usasearch"

ROBOTSTXT_OBEY = True

SCHEDULER_PRIORITY_QUEUE = "scrapy.pqueues.DownloaderAwarePriorityQueue"

CONCURRENT_REQUESTS = 100

REACTOR_THREADPOOL_MAXSIZE = 20

LOG_LEVEL = "INFO"

RETRY_ENABLED = False

DOWNLOAD_TIMEOUT = 180

AJAXCRAWL_ENABLED = True

DEPTH_PRIORITY = 1
SCHEDULER_DISK_QUEUE = "scrapy.squeues.PickleFifoDiskQueue"
SCHEDULER_MEMORY_QUEUE = "scrapy.squeues.FifoMemoryQueue"

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0

CONCURRENT_REQUESTS_PER_DOMAIN = 128

COOKIES_ENABLED = False

MIDDLEWARE_ROOT = "search_gov_crawler.search_gov_spiders.middlewares"
SPIDER_MIDDLEWARES = {
    f"{MIDDLEWARE_ROOT}.SearchGovSpidersSpiderMiddleware": 543,
}

DOWNLOADER_MIDDLEWARES = {
    f"{MIDDLEWARE_ROOT}.SearchGovSpidersDownloaderMiddleware": 543,
}

AUTOTHROTTLE_ENABLED = False

AUTOTHROTTLE_MAX_DELAY = 5

HTTPCACHE_ENABLED = True

HTTPCACHE_DIR = "httpcache"

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

FEEDS = {
    "scrapy_urls/%(name)s/%(name)s_%(time)s.txt": {
        "format": "csv",
    }
}
