import os
import pytest
from unittest.mock import MagicMock
from scrapy import Item
# from search_gov_crawler.search_gov_spiders.pipelines import SearchGovSpidersPipeline

import os
import requests
from pathlib import Path

from scrapy.exceptions import DropItem


class SearchGovSpidersPipeline:
    """
    Pipeline that either writes items to an output file with a max size of 3.9MB
    or, if SPIDER_URLS_API is set, sends a POST request with a list of URLs once
    the size limit is reached.
    """

    MAX_FILE_SIZE_MB = 3.9  # max size in MB
    MAX_FILE_SIZE_BYTES = int(MAX_FILE_SIZE_MB * 1024 * 1024)  # convert to bytes

    def __init__(self, *_args, **_kwargs):
        self.api_url = os.environ.get("SPIDER_URLS_API")
        if not self.api_url:
            self.file_number = 1
            self.parent_file_path = Path(__file__).parent.parent.resolve()
            self.base_file_name = self.parent_file_path / "output" / "all-links.csv"
            self.file_path = self.base_file_name
            self.current_file = open(self.file_path, "w", encoding="utf-8")
        else:
            self.urls_batch = []

    def process_item(self, item, spider):
        """Process item either by writing to file or by posting to API."""

        line = item.get("url", "") + "\n"
        line_size = len(line.encode('utf-8'))

        # If API URL is set, batch URLs and send a POST request when max size is reached
        if self.api_url:
            self.urls_batch.append(item.get("url", ""))
            if self._is_batch_too_large(line_size):
                self._post_urls(spider)
        # Otherwise, write to file and rotate if needed
        else:
            self.current_file.write(line)
            if self._is_file_too_large(line_size):
                self._rotate_file()

        return item

    def _is_batch_too_large(self, new_entry_size):
        current_batch_size = sum(len(url.encode('utf-8')) for url in self.urls_batch)
        return (current_batch_size + new_entry_size) > self.MAX_FILE_SIZE_BYTES

    def _is_file_too_large(self, new_entry_size):
        self.current_file.flush()
        current_file_size = self.file_path.stat().st_size
        return (current_file_size + new_entry_size) > self.MAX_FILE_SIZE_BYTES

    def _rotate_file(self):
        """Close current file, rename it, and open a new one for continued writing."""
        self.current_file.close()
        new_file_path = self.parent_file_path / f"output/all-links-{self.file_number}.csv"
        os.rename(self.file_path, new_file_path)
        self.file_number += 1
        self.current_file = open(self.file_path, "w", encoding="utf-8")

    def _post_urls(self, spider):
        """Send a POST request with the batch of URLs if any exist."""
        if self.urls_batch:
            try:
                response = requests.post(self.api_url, json={"urls": self.urls_batch})
                response.raise_for_status()
                spider.logger.info(f"Successfully posted {len(self.urls_batch)} URLs to {self.api_url}.")
            except requests.exceptions.RequestException as e:
                raise SystemExit(f"Failed to send URLs to {self.api_url}: {e}")
            finally:
                self.urls_batch.clear()

    def close_spider(self, _spider):
        """Close the file or send remaining URLs if needed when the spider finishes."""
        if not self.api_url and self.current_file:
            self.current_file.close()
        elif self.api_url:
            self._post_urls()  # Send any remaining URLs on spider close

class DeDeuplicatorPipeline:
    """Class for pipeline that removes duplicate items"""

    itemlist = []

    def process_item(self, item, _spider):
        """Checks that the file is not at max size.
        Adds it to the file if less, or creates a new file if too large."""
        if item in self.itemlist:
            raise DropItem("already in list")
        self.itemlist.append(item)

        return item


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
