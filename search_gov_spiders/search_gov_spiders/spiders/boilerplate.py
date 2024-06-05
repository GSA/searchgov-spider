import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class BoilerplateSpider(CrawlSpider):
    name = "boilerplate"
    allowed_domains = ["boiler.plate"] #this can be a list
    start_urls = ["https://boiler.plate"] #this can be a list

    #_________________________________________________________
    # ^starting from this line of the new spider, replace the content with the following:

    rules = (Rule(LinkExtractor(allow = (), deny = ["calendar", "location-contact"],unique = True), callback="parse_item", follow=True),)

    def parse_item(self, response):
        yield {
            "Link": response.url
        }