from typing import Optional

from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Response, Request

import search_gov_crawler.search_gov_spiders.helpers.domain_spider as helpers
from search_gov_crawler.search_gov_spiders.items import SearchGovSpidersItem


class DomainSpiderJs(CrawlSpider):
    """
    Main spider for crawling and retrieving URLs using a headless browser to hanlde javascript.
    Will grab single values for url and domain or use multiple comma-separated inputs.
    If nothing is passed, it will crawl using the default list of domains and urls.

    Playwright javascript handling is enabled and resource intensive, only use if needed.  For crawls
    that don't require html, use `domain_spider`.

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
    - ```scrapy crawl domain_spider_js```
    - ```scrapy crawl domain_spider_js \
             -a allowed_domains=test-1.example.com,test-2.example.com \
             -a start_urls=http://test-1.example.com/,https://test-2.example.com/```
    - ```scrapy crawl domain_spider \
             -a allowed_domains=test-3.example.com \
             -a start_urls=http://test-3.example.com/```
    """

    name: str = "domain_spider_js"
    custom_settings: dict = {"PLAYWRIGHT_ABORT_REQUEST": helpers.should_abort_request}

    def __init__(
        self, *args, allowed_domains: Optional[str] = None, start_urls: Optional[str] = None, **kwargs
    ) -> None:
        if any([allowed_domains, start_urls]) and not all([allowed_domains, start_urls]):
            raise ValueError("Invalid arguments: allowed_domains and start_urls must be used together or not at all.")

        super().__init__(*args, **kwargs)

        self.allowed_domains = (
            allowed_domains.split(",") if allowed_domains else helpers.default_allowed_domains(handle_javascript=True)
        )
        self.start_urls = start_urls.split(",") if start_urls else helpers.default_starting_urls(handle_javascript=True)

    rules = (
        Rule(
            link_extractor=helpers.domain_spider_link_extractor,
            callback="parse_item",
            follow=True,
            process_request="set_playwright_usage",
        ),
    )

    def parse_item(self, response: Response):
        """This function gathers the url for valid content-type responses
        @url http://quotes.toscrape.com/
        @returns items 1 1
        @scrapes url
        """
        content_type = response.headers.get("content-type", None)

        if helpers.is_valid_content_type(content_type):
            items = SearchGovSpidersItem()
            items["url"] = response.url
            yield items

    def set_playwright_usage(self, request: Request, _response: Response) -> Request:
        """Set meta tags for playwright to run"""

        request.meta["playwright"] = True
        request.meta["errback"] = request.errback
        return request
