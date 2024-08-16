import json
from collections import namedtuple
from pathlib import Path

import pytest

from search_gov_crawler.search_gov_spiders.helpers import domain_spider as helpers


@pytest.mark.parametrize(
    ("content_type_header", "result"),
    [("text/html", True), ("application/msword.more.and.more", True), ("Something/Else", False)],
    ids=["good", "regex", "bad"],
)
def test_is_valid_content_type(content_type_header, result):
    assert helpers.is_valid_content_type(content_type_header) is result


def test_get_crawl_sites_default():
    assert len(helpers.get_crawl_sites()) == 66


@pytest.fixture(name="crawl_sites_test_file")
def fixture_crawl_sites_test_file():
    return Path(__file__).parent / "crawl-sites-test.json"


@pytest.fixture(name="crawl_sites_test_file_json")
def fixture_crawl_sites_test_file_json(crawl_sites_test_file):
    return json.loads(crawl_sites_test_file.resolve().read_text())


def test_get_crawl_sites_test_file(crawl_sites_test_file):
    assert len(helpers.get_crawl_sites(str(crawl_sites_test_file.resolve()))) == 3


@pytest.mark.parametrize(("handle_javascript", "results"), [(True, 2), (False, 1)])
def test_default_starting_urls(monkeypatch, crawl_sites_test_file_json, handle_javascript, results):
    def mock_get_crawl_sites(*args, **kwargs):
        return crawl_sites_test_file_json

    monkeypatch.setattr(
        "search_gov_crawler.search_gov_spiders.helpers.domain_spider.get_crawl_sites", mock_get_crawl_sites
    )

    starting_urls = helpers.default_starting_urls(handle_javascript)
    assert len(starting_urls) == results


@pytest.mark.parametrize(("handle_javascript", "results"), [(True, 2), (False, 1)])
def test_default_allowed_domains(monkeypatch, crawl_sites_test_file_json, handle_javascript, results):
    def mock_get_crawl_sites(*args, **kwargs):
        return crawl_sites_test_file_json

    monkeypatch.setattr(
        "search_gov_crawler.search_gov_spiders.helpers.domain_spider.get_crawl_sites", mock_get_crawl_sites
    )

    starting_urls = helpers.default_allowed_domains(handle_javascript)
    assert len(starting_urls) == results


Request = namedtuple("Request", ["resource_type", "should_abort"])


@pytest.fixture(name="request_with_resource_type", params=[("jpeg", True), ("html", False)], ids=["Valid", "Invalid"])
def fixture_request_with_resource_type(request) -> Request:
    return Request(*request.param)


def test_should_abort_request(request_with_resource_type):
    assert helpers.should_abort_request(request_with_resource_type) == request_with_resource_type.should_abort
