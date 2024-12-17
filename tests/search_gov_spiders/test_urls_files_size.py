import os
from pathlib import Path

import pytest

from scrapy import Spider
from scrapy.utils.test import get_crawler
from search_gov_crawler.search_gov_spiders.items import SearchGovSpidersItem
from search_gov_crawler.search_gov_spiders.pipelines import SearchGovSpidersPipeline


@pytest.fixture(name="sample_spider")
def fixture_sample_spider():
    crawler = get_crawler(Spider)
    return crawler._create_spider(
        name="urls_test", allowed_domains="example.com", allowed_domain_paths="https://www.example.com"
    )


@pytest.fixture(name="sample_item")
def fixture_sample_item() -> SearchGovSpidersItem:
    """Fixture for a sample item with a URL."""
    item = SearchGovSpidersItem()
    item["url"] = "http://example.com"
    return item


@pytest.fixture(name="mock_open")
def fixture_mock_open(mocker):
    return mocker.patch("builtins.open", mocker.mock_open())


@pytest.fixture(name="pipeline_no_api")
def fixture_pipeline_no_api(mock_open, mocker) -> SearchGovSpidersPipeline:
    mocker.patch.dict(os.environ, {})
    mocker.patch('os.getpid', return_value=1234)
    return SearchGovSpidersPipeline()


@pytest.fixture(name="pipeline_with_api")
def fixture_pipeline_with_api(mocker) -> SearchGovSpidersPipeline:
    """Fixture for pipeline with an API URL set."""
    mocker.patch.dict(os.environ, {"SPIDER_URLS_API": "http://mockapi.com"})
    mocker.patch('os.getpid', return_value=1234)
    return SearchGovSpidersPipeline()


def test_write_to_file(pipeline_no_api, mock_open, sample_item, sample_spider, mocker):
    """Test that URLs are written to files when SPIDER_URLS_API is not set."""
    pipeline_no_api.process_item(sample_item, sample_spider)

    # Ensure file is opened and written to
    mock_open.assert_called_once_with(pipeline_no_api.base_file_name, "w", encoding="utf-8")
    mock_open().write.assert_any_call(sample_item["url"] + "\n")


def test_post_to_api(pipeline_with_api, sample_item, sample_spider, mocker):
    """Test that URLs are batched and sent via POST when SPIDER_URLS_API is set."""
    mock_post = mocker.patch("requests.post")

    pipeline_with_api.process_item(sample_item, sample_spider)

    # Check that the batch contains the URL
    assert sample_item["url"] in pipeline_with_api.urls_batch

    # Simulate max size to force post
    mocker.patch.object(SearchGovSpidersPipeline, "_is_batch_too_large", return_value=True)
    pipeline_with_api.process_item(sample_item, sample_spider)

    # Ensure POST request was made
    mock_post.assert_called_once_with("http://mockapi.com", json={"urls": pipeline_with_api.urls_batch})


def test_rotate_file(pipeline_no_api, mock_open, sample_item, mocker):
    """Test that file rotation occurs when max size is exceeded."""
    mock_rename = mocker.patch("os.rename")

    pipeline_no_api.process_item(sample_item, None)

    # Check if the file was rotated
    mock_open.assert_called_with(pipeline_no_api.base_file_name, "a", encoding="utf-8")
    mock_open().close.assert_called()
    mock_rename.assert_called_once_with(
        pipeline_no_api.file_path, pipeline_no_api.parent_file_path / "output/all-links-1.csv"
    )


def test_post_urls_on_spider_close(pipeline_with_api, sample_spider, mocker):
    """Test that remaining URLs are posted when spider closes and SPIDER_URLS_API is set."""
    mock_post = mocker.patch("requests.post")

    pipeline_with_api.urls_batch = ["http://example.com"]

    pipeline_with_api.close_spider(sample_spider)

    # Ensure POST request was made on spider close, cannot verify json once urls_batch is cleared
    mock_post.assert_called_once_with("http://mockapi.com", json=mocker.ANY)


def test_close_file_on_spider_close(pipeline_no_api, mock_open):
    """Test that the file is closed when the spider closes and no SPIDER_URLS_API is set."""

    pipeline_no_api.close_spider(None)

    # Ensure the file is closed
    mock_open().close.assert_called_once()
