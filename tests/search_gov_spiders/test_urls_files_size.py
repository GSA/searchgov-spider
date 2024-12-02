import os
import pytest
from unittest.mock import MagicMock
from scrapy import Item
from search_gov_crawler.search_gov_spiders.pipelines import SearchGovSpidersPipeline

@pytest.fixture
def sample_item():
    """Fixture for a sample item with a URL."""
    item = Item()
    item['url'] = "http://example.com"
    return item

@pytest.fixture
def pipeline_no_api(mocker):
    """Fixture for pipeline with no API URL set."""
    mocker.patch('os.getenv', return_value=None)
    return SearchGovSpidersPipeline()

@pytest.fixture
def pipeline_with_api(mocker):
    """Fixture for pipeline with an API URL set."""
    mocker.patch('os.getenv', return_value="http://mockapi.com")
    return SearchGovSpidersPipeline()

def test_write_to_file(pipeline_no_api, sample_item, mocker):
    """Test that URLs are written to files when SPIDER_URLS_API is not set."""
    mock_open = mocker.patch('open', mocker.mock_open())

    pipeline_no_api.process_item(sample_item, None)

    # Ensure file is opened and written to
    mock_open.assert_called_once_with(pipeline_no_api.base_file_name, 'w', encoding='utf-8')
    mock_open().write.assert_any_call(sample_item['url'] + "\n")

def test_post_to_api(pipeline_with_api, sample_item, mocker):
    """Test that URLs are batched and sent via POST when SPIDER_URLS_API is set."""
    mock_post = mocker.patch('requests.post')

    pipeline_with_api.process_item(sample_item, None)

    # Check that the batch contains the URL
    assert sample_item['url'] in pipeline_with_api.urls_batch

    # Simulate max size to force post
    mocker.patch.object(SearchGovSpidersPipeline, '_is_batch_too_large', return_value=True)
    pipeline_with_api.process_item(sample_item, None)

    # Ensure POST request was made
    mock_post.assert_called_once_with("http://mockapi.com", json={"urls": pipeline_with_api.urls_batch})

def test_rotate_file(pipeline_no_api, sample_item, mocker):
    """Test that file rotation occurs when max size is exceeded."""
    mock_open = mocker.patch('open', mocker.mock_open())
    mock_rename = mocker.patch('os.rename')

    mocker.patch.object(SearchGovSpidersPipeline, '_is_file_too_large', return_value=True)
    pipeline_no_api.process_item(sample_item, None)

    # Check if the file was rotated
    mock_open.assert_called_with(pipeline_no_api.base_file_name, 'w', encoding='utf-8')
    mock_open().close.assert_called()
    mock_rename.assert_called_once_with(
        pipeline_no_api.file_path,
        pipeline_no_api.parent_file_path / "output/all-links-1.csv"
    )

def test_post_urls_on_spider_close(pipeline_with_api, mocker):
    """Test that remaining URLs are posted when spider closes and SPIDER_URLS_API is set."""
    mock_post = mocker.patch('requests.post')

    pipeline_with_api.urls_batch = ["http://example.com"]

    pipeline_with_api.close_spider(None)

    # Ensure POST request was made on spider close
    mock_post.assert_called_once_with("http://mockapi.com", json={"urls": ["http://example.com"]})

def test_close_file_on_spider_close(pipeline_no_api, mocker):
    """Test that the file is closed when the spider closes and no SPIDER_URLS_API is set."""
    mock_open = mocker.patch('open', mocker.mock_open())

    pipeline_no_api.close_spider(None)

    # Ensure the file is closed
    mock_open().close.assert_called_once()
