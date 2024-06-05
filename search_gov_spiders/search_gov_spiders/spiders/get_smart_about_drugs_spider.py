import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class GetSmartAboutDrugsSpiderSpider (CrawlSpider):
    name = "get_smart_about_drugs_spider"
    allowed_domains = ["getsmartaboutdrugs.gov"]
    start_urls = ["https://getsmartaboutdrugs.gov",
                  "https://www.getsmartaboutdrugs.gov/drugs"]

    rules = (Rule(LinkExtractor(allow = (), unique = True), callback="parse_item", follow=True),)

    def parse_item(self, response):
        yield {
            "Link": response.url
        }