from typing import Optional

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Response, Request

import search_gov_crawler.search_gov_spiders.helpers.domain_spider as helpers
from search_gov_crawler.search_gov_spiders.items import SearchGovSpidersItem


class DomainSpider(CrawlSpider):
    """
    Main spider for crawling and retrieving URLs.  Will grab single values for url and domain
    or use multiple comma-separated inputs.  If nothing is passed, it will crawl using the default list of
    domains and urls.

    Playwright javascript handling is disabled, use `domain_spider_js` for site that need to handle javascript.

    To use the CLI for crawling domain/site follow the pattern below.  The desired domains and urls can
    be either single values or comma separated lists.

    `scrapy crawl domain_spider -a allowed_domains=<desired_domains> -a start_urls=<desired_urls>`

    Examples:
    Class Arguments
    - `allowed_domains="test-1.example.com,test-2.example.com"`
    - `start_urls="http://test-1.example.com/,https://test-2.example.com/"`

    - `allowed_domains="test-3.example.com"`
    - `start_urls="http://test-3.example.com/"`

    CLI Usage
    - ```scrapy crawl domain_spider```
    - ```scrapy crawl domain_spider \
             -a allowed_domains=test-1.example.com,test-2.example.com \
             -a start_urls=http://test-1.example.com/,https://test-2.example.com/```
    - ```scrapy crawl domain_spider \
             -a allowed_domains=test-3.example.com \
             -a start_urls=http://test-3.example.com/```
    """

    name: str = "domain_spider"
    url_map: set[str] = set()
    handle_javascript: bool = False

    def __init__(
        self, *args, allowed_domains: Optional[str] = None, start_urls: Optional[str] = None, **kwargs
    ) -> None:
        if any([allowed_domains, start_urls]) and not all([allowed_domains, start_urls]):
            raise ValueError("Invalid arguments: allowed_domains and start_urls must be used together or not at all.")

        super().__init__(*args, **kwargs)

        self.allowed_domains = (
            allowed_domains.split(",")
            if allowed_domains
            else helpers.default_allowed_domains(handle_javascript=self.handle_javascript)
        )
        self.start_urls = (
            start_urls.split(",")
            if start_urls
            else helpers.default_starting_urls(handle_javascript=self.handle_javascript)
        )

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
                deny_extensions=helpers.FILTER_EXTENSIONS,
                unique=True,
            ),
            callback="parse_item",
            follow=True,
            process_request="set_playwright_usage",
        ),
    )

    def parse_item(self, response: Response):
        """This function gathers the url and the status.
        @url http://quotes.toscrape.com/
        @returns items 1 1
        @scrapes url
        """
        content_type = response.headers.get("content-type", None)

        if helpers.is_valid_content_type(content_type) and response.url not in self.url_map:
            self.url_map.add(response.url)
            items = SearchGovSpidersItem()
            items["url"] = response.url
            yield items

    def set_playwright_usage(self, request: Request, _response: Response) -> Request:
        """
        Set meta tags for playwright to run, depending on class variable set on spider.
        Note: this seems to work for js rendering but it is resource and time heavy
        """

        if self.handle_javascript:
            request.meta["playwright"] = True
            request.meta["errback"] = request.errback
        return request


class DomainSpiderJS(DomainSpider):
    """
    Extends DomainSpider so that we can extract links from sites using javascript
    """

    name: str = "domain_spider_js"
    custom_settings: dict = {"PLAYWRIGHT_ABORT_REQUEST": helpers.should_abort_request}
    handle_javascript: bool = True
