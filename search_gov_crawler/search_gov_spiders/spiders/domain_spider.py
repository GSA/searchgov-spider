from typing import Optional

from scrapy.spiders import CrawlSpider, Rule

import search_gov_crawler.search_gov_spiders.helpers.domain_spider as helpers


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

    def __init__(
        self, *args, allowed_domains: Optional[str] = None, start_urls: Optional[str] = None, **kwargs
    ) -> None:
        if any([allowed_domains, start_urls]) and not all([allowed_domains, start_urls]):
            raise ValueError("Invalid arguments: allowed_domains and start_urls must be used together or not at all.")

        super().__init__(*args, **kwargs)

        self.allowed_domains = (
            allowed_domains.split(",") if allowed_domains else helpers.default_allowed_domains(handle_javascript=False)
        )
        self.start_urls = (
            start_urls.split(",") if start_urls else helpers.default_starting_urls(handle_javascript=False)
        )

    rules = (Rule(link_extractor=helpers.domain_spider_link_extractor, callback=helpers.parse_item, follow=True),)
