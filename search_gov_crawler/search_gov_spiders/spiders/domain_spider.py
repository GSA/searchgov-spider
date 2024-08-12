from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..items import SearchGovSpidersItem
from . import domain_spider_helper_variables as helper_variables
from . import domain_spider_helper_functions as helper_functions

# scrapy command for crawling domain/site
# scrapy crawl domain_spider -a domain=desired_domain -a urls=desired_url
# ex: ... -a domain=travel.dod.mil -a urls=https://travel.dod.mil

from scrapy.http import Response
import re
from ..items import SearchGovSpidersItem


def valid_content_type(type_whitelist, content_type_header):
    content_type_header = str(content_type_header)
    for type_regex in type_whitelist:
        if re.search(type_regex, content_type_header):
            return True
    return False


class DomainSpider(CrawlSpider):
    name = "domain_spider"
    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": helper_functions.should_abort_request
    }

    def __init__(self, domain: str = None, urls: str = None, *args, **kwargs):
        super(DomainSpider, self).__init__(*args, **kwargs)
        # will grab singular domain
        # multiple comma-separated inputs:
        #   ex: domain=getsmartaboutdrugs.gov,travel.dod.mil
        # or the list of search.gov domains
        self.allowed_domains = domain.split(",") if domain \
            else helper_variables.domains_list
        # urls to start crawling from in domain(s)
        # will grab singular start url
        # multiple comma-separated inputs:
        #   ex: urls=https://getsmartaboutdrugs.gov,https://travel.dod.mil
        # or the list of search.gov start urls
        self.start_urls = urls.split(",") if urls \
            else helper_variables.start_urls_list
        self.url_map = {}

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

    def parse_item(self, response: Response):
        """This function gathers the url and the status.
        @url http://quotes.toscrape.com/
        @returns items 1 2
        @returns requests 0 0
        @scrapes Status Link
        """
        content_type = response.headers.get("content-type", None)
        allowed_type = helper_variables.ALLOWED_CONTENT_TYPE
        if valid_content_type(allowed_type, content_type) and \
                response.url not in self.url_map:
            self.url_map[response.url] = True
            items = SearchGovSpidersItem()
            items["url"] = response.url
            yield items
