import os
import sys

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..items import SearchGovSpidersItem

# scrapy command for crawling domain/site
# scrapy crawl domain_spider -a domain=desired_domain -a urls=desired_url
# ex: scrapy crawl domain_spider -a domain=travel.dod.mil -a urls=https://travel.dod.mil

starting_urls = os.path.join(
    os.path.dirname(sys.modules[__name__].__file__), "../utility_files/startingUrls.txt"
)

start_urls_list = []
with open(starting_urls, encoding="utf-8") as file:
    while line := file.readline():
        start_urls_list.append(line.rstrip())

domains = os.path.join(
    os.path.dirname(sys.modules[__name__].__file__), "../utility_files/domains.txt"
)

domains_list = []
with open(domains, encoding="utf-8") as file:
    while line := file.readline():
        domains_list.append(line.rstrip())


PLAYWRIGHT_FLAG = True


# needed for meta tag for playwright to be added
# note: this seems to work for js rendering but it is resource and time heavy
def set_playwright_true(request, response):
    if PLAYWRIGHT_FLAG:
        request.meta["playwright"] = True
        request.meta["playwright_include_page"] = True
        request.meta["errback"] = request.errback
    # We can use below to wait for certain items on a page to load.
    # But not sure what would be a good thing on all pages.
    # This is for js rendering - https://scrapeops.io/python-scrapy-playbook/scrapy-playwright/
    # request.meta["playwright_page_methods"] =[PageMethod('wait_for_selector', 'div.quote')],
    return request


# fmt: off
filter_extensions = [
    "cfm","css","eventsource","exe","fetch","font","gif",
    "ibooks","ics","image","jpeg","jpg","js","manifest",
    "media","mp3","mp4","nc","png","ppt","pptx",
    "prj","rss","sfx","stylesheet","svg","tar.gz","tar",
    "tif","wav","websocket","wmv","xhr","xml","zip",]
# fmt: on


def should_abort_request(request):
    if request.resource_type in filter_extensions:
        return True
    return False


class DomainSpider(CrawlSpider):
    name = "domain_spider"
    custom_settings = {"PLAYWRIGHT_ABORT_REQUEST": should_abort_request}

    def __init__(self, *args, domain=None, urls=None, **kwargs):
        super(DomainSpider, self).__init__(*args, **kwargs)
        # will grab singular domain
        # multiple comma-separated inputs
        # (ex input: domain=getsmartaboutdrugs.gov,travel.dod.mil)
        # or the list of search.gov domains
        if domain and "," in domain:
            self.allowed_domains = domain.split(",")
        else:
            self.allowed_domains = [domain] if domain else domains_list

        # urls to start crawling from in domain(s)
        # will grab singular start url
        # multiple comma-separated inputs
        # (ex input: urls=https://getsmartaboutdrugs.gov,https://travel.dod.mil)
        # or the list of search.gov start urls
        if urls and "," in urls:
            self.start_urls = urls.split(",")
        else:
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
                deny_extensions=filter_extensions,
                unique=True,
            ),
            callback="parse_item",
            follow=True,
            process_request=set_playwright_true,
        ),
    )

    async def parse_item(self, response):
        """This function gathers the url and the status.

        @url http://quotes.toscrape.com/
        @returns items 1 2
        @returns requests 0 0
        @scrapes Status Link
        """

        if PLAYWRIGHT_FLAG:
            page = response.meta["playwright_page"]
            await page.close()
        items = SearchGovSpidersItem()
        items["url"] = response.url
        yield items

    async def errback(self, failure):
        if PLAYWRIGHT_FLAG:
            page = failure.request.meta["playwright_page"]
            await page.close()
