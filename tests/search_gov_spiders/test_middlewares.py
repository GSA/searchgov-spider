import pytest

from scrapy import Request, Spider
from scrapy.exceptions import IgnoreRequest
from scrapy.utils.test import get_crawler
from search_gov_crawler.search_gov_spiders.middlewares import (
    SearchGovSpidersOffsiteMiddleware,
    SearchGovSpidersDownloaderMiddleware,
)


MIDDLEWARE_TEST_CASES = [
    (["example.com"], ["example.com"], "http://www.example.com/1", True),
    (["sub.example.com"], ["sub.example.com"], "http://sub.example.com/1", True),
    (["sub.example.com"], ["sub.example.com"], "http://www.example.com/1", False),
    (["example.com"], ["example.com/path"], "http://example.com/1", False),
    (["sub.example.com"], ["sub.example.com/path/"], "http://sub.example.com/path/more/more", True),
    (["sub.example.com"], ["sub.example.com/path/"], "http://sub.example.com/path/1", True),
    (["example.com"], None, "http://www.example.com/2", True),
    (["example.com"], [None], "http://www.example.com/2", True),
]


@pytest.mark.parametrize(("allowed_domain", "allowed_domain_path", "url", "allowed"), MIDDLEWARE_TEST_CASES)
def test_offsite_process_request_domain_filtering(allowed_domain, allowed_domain_path, url, allowed):
    # pylint: disable=protected-access
    crawler = get_crawler(Spider)
    spider = crawler._create_spider(
        name="offsite_test", allowed_domains=allowed_domain, allowed_domain_paths=allowed_domain_path
    )
    mw = SearchGovSpidersOffsiteMiddleware.from_crawler(crawler)
    mw.spider_opened(spider)
    request = Request(url)
    if allowed:
        assert mw.process_request(request, spider) is None
    else:
        with pytest.raises(IgnoreRequest):
            mw.process_request(request, spider)


INVALID_DOMAIN_TEST_CASES = [
    (
        ["example.com"],
        ["http://www.example.com"],
        (
            "allowed_domain_paths accepts only domains, not URLs. "
            "Ignoring URL entry http://www.example.com in allowed_domain_paths."
        ),
    ),
    (
        ["example.com"],
        ["example.com:443"],
        (
            "allowed_domain_paths accepts only domains without ports. "
            "Ignoring entry example.com:443 in allowed_domain_paths."
        ),
    ),
]


@pytest.mark.parametrize(("allowed_domain", "allowed_domain_path", "warning_message"), INVALID_DOMAIN_TEST_CASES)
def test_offsite_invalid_domain_paths(allowed_domain, allowed_domain_path, warning_message):
    # pylint: disable=protected-access
    crawler = get_crawler(Spider)
    spider = crawler._create_spider(
        name="offsite_test", allowed_domains=allowed_domain, allowed_domain_paths=allowed_domain_path
    )
    mw = SearchGovSpidersOffsiteMiddleware.from_crawler(crawler)

    with pytest.warns(UserWarning, match=warning_message):
        mw.spider_opened(spider)

    request = Request("http://www.example.com")
    assert mw.process_request(request, spider) is None


def test_spider_downloader_middleware():
    # pylint: disable=protected-access
    crawler = get_crawler(Spider)
    spider = crawler._create_spider(name="test", allowed_domains="example.com")
    mw = SearchGovSpidersDownloaderMiddleware.from_crawler(crawler)

    mw.spider_opened(spider)
    request = Request("http://www.example.com/test?parm=value")

    with pytest.raises(IgnoreRequest):
        mw.process_request(request=request, spider=spider)
