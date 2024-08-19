import json
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from betamax import Betamax
import pytest
from scrapy.crawler import CrawlerProcess
from scrapy import http
from scrapy.exceptions import IgnoreRequest
from scrapy.utils.project import get_project_settings

from search_gov_crawler.search_gov_spiders.helpers.domain_spider import parse_item
from search_gov_crawler.search_gov_spiders.spiders.domain_spider import DomainSpider
from search_gov_crawler.search_gov_spiders.spiders.domain_spider_js import DomainSpiderJs


with Betamax.configure() as config:
    config.cassette_library_dir = str(Path(__file__).parent / "responses")
    config.preserve_exact_body_bytes = True

pytest.mark.usefixtures("betamax_session")


class TestSpiderCrawl:
    @pytest.fixture(params=[DomainSpider, DomainSpiderJs])
    def spider(self, request):
        return request.param(allowed_domains="quotes.toscrape.com", start_urls="https://quotes.toscrape.com")

    def test_parse_item(self, spider, betamax_session):
        response = betamax_session.get(spider.start_urls[0])
        scrapy_response = http.Response(body=response.content, url=spider.start_urls[0], headers=response.headers)

        items = list(parse_item(scrapy_response))
        assert items == [{"url": "https://quotes.toscrape.com"}]

    def test_link_extractor(self, spider, betamax_session):
        response = betamax_session.get(spider.start_urls[0])
        scrapy_response = http.TextResponse(body=response.content, url=spider.start_urls[0], headers=response.headers)

        links = list(spider.rules[0].link_extractor.extract_links(scrapy_response))

        assert len(links) == 49  # unique links from first page


class TestSpiderFullCrawl:
    def test_crawl(self, monkeypatch, betamax_session):
        def mock_process_request(*args, **kwargs):
            if kwargs:
                request = kwargs["request"]
            else:
                request = args[0]

            if urlparse(request.url).query:
                raise IgnoreRequest

            # response = betamax_session.get(request.url)
            # return http.TextResponse(
            #    body=response.content,
            #    url=request.url,
            #    headers=response.headers,
            # )

            return None

        monkeypatch.setenv("SCRAPY_SETTINGS_MODULE", "search_gov_crawler.search_gov_spiders.settings")
        monkeypatch.setattr(
            "search_gov_crawler.search_gov_spiders.middlewares.SearchGovSpidersDownloaderMiddleware.process_request",
            mock_process_request,
        )

        settings = get_project_settings()
        settings.set("SPIDER_MODULES", ["search_gov_crawler.search_gov_spiders.spiders"])

        settings.set(
            "SPIDER_MIDDLEWARES",
            {f"search_gov_crawler.{k}": v for k, v in dict(settings.get("SPIDER_MIDDLEWARES").attributes).items()},
        )
        settings.set(
            "DOWNLOADER_MIDDLEWARES",
            {f"search_gov_crawler.{k}": v for k, v in dict(settings.get("DOWNLOADER_MIDDLEWARES").attributes).items()},
        )

        settings.delete("ITEM_PIPELINES")

        with tempfile.NamedTemporaryFile(suffix=".json") as output_file:
            settings.set("FEEDS", {output_file.name: {"format": "json"}})

            process = CrawlerProcess(settings)
            process.crawl(DomainSpider, allowed_domains="quotes.toscrape.com", start_urls="https://quotes.toscrape.com")

            process.start()

            with open(output_file.name, encoding="UTF") as f:
                links = json.load(f)

            assert len(links) == 378
