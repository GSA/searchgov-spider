import json
import tempfile
import sys
from pathlib import Path

import pytest

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from search_gov_crawler.search_gov_spiders.spiders.domain_spider import DomainSpider
from search_gov_crawler.search_gov_spiders.spiders.domain_spider_js import DomainSpiderJs


@pytest.fixture(name="mock_scrapy_settings")
def fixture_mock_scrapy_settings(monkeypatch):
    # setup for test run
    monkeypatch.setenv("SCRAPY_SETTINGS_MODULE", "search_gov_crawler.search_gov_spiders.settings")

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
    settings.set("HTTPCACHE_ENABLED", True)
    settings.set("HTTPCACHE_DIR", Path(__file__).parent.joinpath("scrapy_httpcache"))
    settings.set("HTTPCACHE_STORAGE", "scrapy.extensions.httpcache.DbmCacheStorage")

    yield settings

    # tear down between runs
    try:
        del sys.modules["twisted.internet.reactor"]
        del sys.modules["twisted.internet"]
    except KeyError:
        pass


FULL_CRAWL_TEST_CASES = [
    (
        DomainSpider,
        False,
        {"allowed_domains": "quotes.toscrape.com", "start_urls": "https://quotes.toscrape.com/"},
        378,
    ),
    (
        DomainSpiderJs,
        True,
        {"allowed_domains": "quotes.toscrape.com", "start_urls": "https://quotes.toscrape.com/js/"},
        388,
    ),
]


@pytest.mark.parametrize(("spider", "use_item_pipeline", "crawl_kwargs", "expected_results"), FULL_CRAWL_TEST_CASES)
def test_full_crawl(mock_scrapy_settings, spider, use_item_pipeline, crawl_kwargs, expected_results):
    if use_item_pipeline:
        mock_scrapy_settings.set(
            "ITEM_PIPELINES",
            {
                f"search_gov_crawler.{k}": v
                for k, v in dict(mock_scrapy_settings.get("ITEM_PIPELINES")).items()
                if k != "search_gov_spiders.pipelines.SearchGovSpidersPipeline"
            },
        )
    else:
        mock_scrapy_settings.delete("ITEM_PIPELINES")

    with tempfile.NamedTemporaryFile(suffix=".json") as output_file:
        mock_scrapy_settings.set("FEEDS", {output_file.name: {"format": "json"}})

        process = CrawlerProcess(mock_scrapy_settings)
        process.crawl(spider, **crawl_kwargs)
        process.start()

        with open(output_file.name, encoding="UTF") as f:
            links = json.load(f)

        assert len(links) == expected_results
