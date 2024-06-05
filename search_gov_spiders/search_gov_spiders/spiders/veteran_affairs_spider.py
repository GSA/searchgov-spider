import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class VeteranAffairsSpiderSpider(CrawlSpider):
    name = "veteran_affairs_spider"
    allowed_domains = ["www.va.gov"]
    start_urls = ["https://www.va.gov/"]

    rules = (Rule(LinkExtractor(allow = (), deny = ["calendar", "thisWeek", "thisYear","monthview"],unique = True), callback="parse_item", follow=True),)

    def parse_item(self, response):
        yield {
            "Link": response.url
        }
