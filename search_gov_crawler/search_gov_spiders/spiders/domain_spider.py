from scrapy.http import Response
from scrapy.spiders import CrawlSpider, Rule

import search_gov_crawler.search_gov_spiders.helpers.domain_spider as helpers
import search_gov_crawler.search_gov_spiders.helpers.encoding as encoding
from search_gov_crawler.search_gov_spiders.items import SearchGovSpidersItem


class DomainSpider(CrawlSpider):
    """
    Main spider for crawling and retrieving URLs.  Will grab single values for url and domain
    or use multiple comma-separated inputs.  If nothing is passed, it will crawl using the default list of
    domains and urls.  Supports path filtering of domains by extending the built-in OffsiteMiddleware. Has
    the ability to allow URLs with query string parameters if desired.

    Playwright javascript handling is disabled, use `domain_spider_js` for site that need to handle javascript.

    To use the CLI for crawling domain/site follow the pattern below.  The desired domains and urls can
    be either single values or comma separated lists. An optional allow_query_string parameter can also
    be passed. The default is false.

    `scrapy crawl domain_spider -a allowed_domains=<desired_domains> -a start_urls=<desired_urls>`

    Examples:
    Class Arguments
    - `allowed_domains="test-1.example.com,test-2.example.com"`
    - `start_urls="http://test-1.example.com/,https://test-2.example.com/"`

    - `allowed_domains="test-3.example.com"`
    - `start_urls="http://test-3.example.com/"`

    - `allow_query_string=true`
    - `allowed_domains="test-4.example.com"`
    - `start_urls="http://test-4.example.com/"`

    CLI Usage
    - ```scrapy crawl domain_spider```
    - ```scrapy crawl domain_spider \
             -a allowed_domains=test-1.example.com,test-2.example.com \
             -a start_urls=http://test-1.example.com/,https://test-2.example.com/```
    - ```scrapy crawl domain_spider \
             -a allowed_domains=test-3.example.com \
             -a start_urls=http://test-3.example.com/```
    - ```scrapy crawl domain_spider \
             -a allow_query_string=true \
             -a allowed_domains=test-4.example.com \
             -a start_urls=http://test-4.example.com/```
    """

    name: str = "domain_spider"
    rules = (Rule(link_extractor=helpers.domain_spider_link_extractor, callback="parse_item", follow=True),)

    def __init__(
        self,
        *args,
        allow_query_string: bool = False,
        allowed_domains: str | None = None,
        start_urls: str | None = None,
        output_target: str | None = None,
        domain_name: str | None = None,
        **kwargs,
    ) -> None:
        if any([allowed_domains, start_urls]) and not all([allowed_domains, start_urls]):
            raise ValueError("Invalid arguments: allowed_domains and start_urls must be used together or not at all.")

        super().__init__(*args, **kwargs)

        self.allow_query_string = allow_query_string

        self.output_target = output_target
        
        self.domain_name = domain_name

        self.allowed_domains = (
            helpers.split_allowed_domains(allowed_domains)
            if allowed_domains
            else helpers.default_allowed_domains(handle_javascript=False)
        )

        self.allowed_domain_paths = (
            allowed_domains.split(",")
            if allowed_domains
            else helpers.default_allowed_domains(handle_javascript=False, remove_paths=False)
        )

        self.start_urls = (
            start_urls.split(",") if start_urls else helpers.default_starting_urls(handle_javascript=False)
        )

    def parse_item(self, response: Response):
        """
        This method is called by spiders to gather the url.  Placed in the spider to assist with
        testing and validtion.

        @url http://quotes.toscrape.com/
        @returns items 1 1
        @scrapes url
        """

        if helpers.is_valid_content_type(response.headers.get("content-type", None), output_target=self.output_target):
            html_content = encoding.decode_http_response(response_bytes=response.body)
            yield SearchGovSpidersItem(url=response.url, html_content=html_content, output_target=self.output_target, domain_name=self.domain_name)
