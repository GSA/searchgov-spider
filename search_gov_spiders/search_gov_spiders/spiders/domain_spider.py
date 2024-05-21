from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

starting_urls = "../utility_files/startingUrls.txt"

start_urls_list = []
with open(starting_urls) as file:
    while line := file.readline():
        start_urls_list.append(line.rstrip())

domains = "../utility_files/domains.txt"
domains_list = []
with open(domains) as file:
    while line := file.readline():
        domains_list.append(line.rstrip())


# scrapy command for crawling domain/site
# scrapy crawl domain_spider -a domain=desired_domain -a urls=desired_url
# ex: scrapy crawl domain_spider -a domain=travel.dod.mil -a urls=https://travel.dod.mil


class DomainSpider(CrawlSpider):
    # name = "travelDodMil"
    name = "domain_spider"

    def __init__(self, domain=None, urls=None, *args, **kwargs):
        super(DomainSpider, self).__init__(*args, **kwargs)
        self.allowed_domains = [domain] if domain else domains_list
        self.start_urls = [urls] if urls else start_urls_list

    # file type exclusions
    rules = (
        Rule(
            LinkExtractor(
                allow=(),
                deny=[
                    "calendar",
                    "location-contact",
                    "DTMO-Site-Map/FileId/",
                    # "\*redirect"
                ],
                deny_extensions=[
                    "js",
                    "xml",
                    "gif",
                    "wmv",
                    "wav",
                    "ibooks",
                    "zip",
                    "css",
                    "mp3",
                    "mp4",
                    "cfm",
                    "jpg",
                    "jpeg",
                    "png",
                    "exe",
                    "svg",
                    "ppt",
                    "pptx",
                    "ics",
                    "nc",
                    "tif",
                    "prj",
                    "tar",
                    "tar.gz",
                    "rss",
                    "sfx",
                ],
                unique=True,
            ),
            callback="parse_item",
            follow=True,
        ),
    )

    @staticmethod
    def parse_item(response):
        """This function gathers the url and the status.

        @url http://quotes.toscrape.com/
        @returns items 1 2
        @returns requests 0 0
        @scrapes Status Link
        """
        yield {"Link": response.url}
