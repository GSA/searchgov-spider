import pytest
from scrapy.http import Response, Request
from search_gov_crawler.search_gov_spiders.spiders.domain_spider import DomainSpider

TEST_URL = "http://example.com"


@pytest.fixture(name="spider")
def fixture_spider():
    return DomainSpider()


def get_results(spider, content: str):
    request = Request(url=TEST_URL, encoding="utf-8")

    response = Response(url=TEST_URL, request=request, headers={"content-type": content})

    spider.allowed_domains = ["example.com"]
    return next(spider.parse_item(response), None)


def test_valid_content(spider):
    spider.url_map = set()
    results = get_results(spider, "text/html")
    assert results is not None and results.get("url") == TEST_URL


def test_valid_content_plus(spider):
    spider.url_map = set()
    results = get_results(spider, "text/html;utf-8")
    assert results is not None and results.get("url") == TEST_URL


def test_invalid_content(spider):
    spider.url_map = set()
    results = get_results(spider, "media/image")
    assert results is None
