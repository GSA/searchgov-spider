import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class JamesWebbSpider(CrawlSpider):
    name = "james_webb_spider"
    allowed_domains = ["nasa.gov"]
    start_urls = ["https://www.jwst.nasa.gov/"]

    rules = (
        Rule(
            LinkExtractor(
                allow=(),
                deny=["calendar", "location-contact"],
                unique=True,
            ),
            callback="parse_item",
            follow=True,
        ),
    )

    # only including "url": response.url and not another response argument throws error
    def parse_item(self, response):
        yield {"Link": response.url, "h1": response.xpath("//h1/text()").get()}
