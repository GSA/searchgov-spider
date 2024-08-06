from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..items import SearchGovSpidersItem
from . import domain_spider_helper_variables as helper_variables
from . import domain_spider_helper_functions as helper_functions

# scrapy command for crawling domain/site
# scrapy crawl domain_spider -a domain=desired_domain -a urls=desired_url
# ex: scrapy crawl domain_spider -a domain=travel.dod.mil -a urls=https://travel.dod.mil


class DomainSpider(CrawlSpider):
    name = "domain_spider"
    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": helper_functions.should_abort_request
    }

    def __init__(self, *args, domain=None, urls=None, **kwargs):
        super(DomainSpider, self).__init__(*args, **kwargs)
        # will grab singular domain
        # multiple comma-separated inputs
        # (ex input: domain=getsmartaboutdrugs.gov,travel.dod.mil)
        # or the list of search.gov domains
        if domain and "," in domain:
            self.allowed_domains = domain.split(",")
        else:
            self.allowed_domains = [domain] if domain else helper_variables.domains_list

        # urls to start crawling from in domain(s)
        # will grab singular start url
        # multiple comma-separated inputs
        # (ex input: urls=https://getsmartaboutdrugs.gov,https://travel.dod.mil)
        # or the list of search.gov start urls
        if urls and "," in urls:
            self.start_urls = urls.split(",")
        else:
            self.start_urls = [urls] if urls else helper_variables.start_urls_list

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
                deny_extensions=helper_variables.filter_extensions,
                unique=True,
            ),
            callback="parse_item",
            follow=True,
            process_request=helper_functions.set_playwright_true,
        ),
    )

    async def parse_item(self, response):
        """This function gathers the url and the status.

        @url http://quotes.toscrape.com/
        @returns items 1 2
        @returns requests 0 0
        @scrapes Status Link
        """

        items = SearchGovSpidersItem()
        items["url"] = response.url
        yield items
