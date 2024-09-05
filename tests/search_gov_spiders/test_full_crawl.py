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
    settings.set("HTTPCACHE_DBM_MODULE", "dbm.dumb")
    settings.set("HTTPCACHE_DIR", Path(__file__).parent.joinpath("scrapy_httpcache"))
    settings.set("HTTPCACHE_STORAGE", "scrapy.extensions.httpcache.DbmCacheStorage")

    # Ensures cache does not change, set to False if you need to update or replace cache files
    settings.set("HTTPCACHE_IGNORE_MISSING", True)

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


@pytest.mark.parametrize(("spider", "use_dedup", "crawl_kwargs", "expected_results"), FULL_CRAWL_TEST_CASES)
def test_full_crawl(mock_scrapy_settings, monkeypatch, spider, use_dedup, crawl_kwargs, expected_results):
    # only use dedup pipeline for js test, otherwise dupes are not cleared between runs
    mock_scrapy_settings.set(
        "ITEM_PIPELINES",
        {
            f"search_gov_crawler.{k}": v
            for k, v in dict(mock_scrapy_settings.get("ITEM_PIPELINES")).items()
            if (k == "search_gov_spiders.pipelines.SearchGovSpidersPipeline" or use_dedup)
        },
    )

    with tempfile.NamedTemporaryFile(suffix=".json") as output_file:
        temp_dir = Path(str(output_file.name)).parent
        temp_dir.joinpath("output").mkdir(exist_ok=True)

        def mock_init(pipeline_cls, *_args, temp_dir=temp_dir, **_kwargs):
            pipeline_cls.current_file_size = 0
            pipeline_cls.file_number = 1
            pipeline_cls.parent_file_path = temp_dir
            pipeline_cls.base_path_name = str(pipeline_cls.parent_file_path / "output/all-links.csv")
            pipeline_cls.short_file = open(pipeline_cls.base_path_name, "w", encoding="utf-8")
            pipeline_cls.max_file_size = 3900
            pipeline_cls.paginate = True

        monkeypatch.setattr(
            "search_gov_crawler.search_gov_spiders.pipelines.SearchGovSpidersPipeline.__init__", mock_init
        )

        mock_scrapy_settings.set("FEEDS", {output_file.name: {"format": "json"}})

        process = CrawlerProcess(mock_scrapy_settings)
        process.crawl(spider, **crawl_kwargs)
        process.start()

        with open(output_file.name, encoding="UTF") as f:
            links = json.load(f)

        split_files = list(temp_dir.glob("all-links*.csv"))

        # verify total links match expected
        assert len(links) == expected_results

        # verify split files exist and are under max file size
        assert all(split_file.stat().st_size < 3900 for split_file in split_files)