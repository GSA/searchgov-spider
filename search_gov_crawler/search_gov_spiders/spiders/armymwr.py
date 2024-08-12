import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class ArmymwrSpider(CrawlSpider):
    name = "armymwr"
    allowed_domains = ["armymwr.com"]
    start_urls = ["https://www.armymwr.com/"]

    rules = (
        Rule(
            LinkExtractor(
                allow=(),
                deny=[
                    "calendar",
                    "location-contact",
                    "DTMO-Site-Map/FileId/",
                    r"\*.js",
                    r"\*redirect",
                    r"\*.xml",
                    r"\*.gif",
                    r"\*.wmv",
                    r"\*.wav",
                    r"\*.ibooks",
                    r"\*.zip",
                    r"\*.css",
                    r"\*.mp3",
                    r"\*.mp4",
                    r"\*.cfm",
                    r"\*.jpg",
                    r"\*.jpeg",
                    r"\*.png",
                    r"\*.svg",
                ],
                unique=True,
            ),
            callback="parse_item",
            follow=True,
        ),
    )

    def parse_item(self, response):
        yield {"Link": response.url}
