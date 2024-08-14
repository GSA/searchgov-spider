import pytest
from scrapy.http import Response, Request
from ..spiders.domain_spider import DomainSpider

TEST_URL = "http://example.com"


@pytest.fixture
def spider():
    return DomainSpider()


def get_results(spider, content: str):
    request = Request(url=TEST_URL, encoding="utf-8")

    response = Response(
        url=TEST_URL,
        request=request,
        headers={"content-type": content}
    )

    spider.allowed_domains = ["example.com"]
    return next(spider.parse_item(response), None)


def test_valid_content(spider):
    results = get_results(spider, "text/html")
    assert results != None and results.get("url") == TEST_URL


def test_valid_content_plus(spider):
    results = get_results(spider, "text/html;utf-8")
    assert results != None and results.get("url") == TEST_URL


def test_invalid_content(spider):
    results = get_results(spider, "media/image")
    assert results == None
