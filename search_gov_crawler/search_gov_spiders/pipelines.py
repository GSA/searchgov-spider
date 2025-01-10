"""Define your item pipelines here
Don't forget to add your pipeline to the ITEM_PIPELINES setting
See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
"""
import os
from pathlib import Path
import requests
from scrapy.exceptions import DropItem


class SearchGovSpidersPipeline:
    """
    Pipeline that writes items to files (rotated at ~3.9MB) or sends batched POST requests
    to SPIDER_URLS_API if the environment variable is set.
    """

    MAX_FILE_SIZE_BYTES = int(1024 * 1024)  # 1MB in bytes
    BATCH_SIZE = 100  # Maximum number of URLs before sending a batch request
    APP_PID = os.getpid()

    def __init__(self):
        self.api_url = os.environ.get("SPIDER_URLS_API")
        self.urls_batch = []
        self.file_number = 1
        self.file_path = None
        self.current_file = None

        if not self.api_url:
            output_dir = Path(__file__).parent.parent / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            base_filename = f"all-links-p{self.APP_PID}"
            self.file_path = output_dir / f"{base_filename}.csv"
            self.current_file = open(self.file_path, "a", encoding="utf-8")

    def process_item(self, item, spider):
        """Handle each item by writing to file or batching URLs for an API POST."""
        url = item.get("url", "")
        if not url:
            raise DropItem("Missing URL in item")

        if self.api_url:
            self._process_api_item(url, spider)
        else:
            self._process_file_item(url)

        return item

    def _process_api_item(self, url, spider):
        """Batch URLs for API and send POST if size or count limit is reached."""
        self.urls_batch.append(url)
        if len(self.urls_batch) >= self.BATCH_SIZE or self._batch_size() >= self.MAX_FILE_SIZE_BYTES:
            self._send_post_request(spider)

    def _process_file_item(self, url):
        """Write URL to file and rotate the file if size exceeds the limit."""
        self.current_file.write(f"{url}\n")
        if self._file_size() >= self.MAX_FILE_SIZE_BYTES:
            self._rotate_file()

    def _batch_size(self):
        """Calculate total size of the batched URLs."""
        return sum(len(url.encode("utf-8")) for url in self.urls_batch)

    def _file_size(self):
        """Get the current file size."""
        self.current_file.flush()  # Ensure the OS writes buffered data to disk
        return self.file_path.stat().st_size

    def _rotate_file(self):
        """Close the current file, rename it, and open a new one."""
        self.current_file.close()
        rotated_file = self.file_path.with_name(f"{self.file_path.stem}-{self.file_number}.csv")
        os.rename(self.file_path, rotated_file)
        self.current_file = open(self.file_path, "a", encoding="utf-8")
        self.file_number += 1

    def _send_post_request(self, spider):
        """Send a POST request with the batched URLs."""
        if not self.urls_batch:
            return

        try:
            response = requests.post(self.api_url, json={"urls": self.urls_batch})
            response.raise_for_status()
            spider.logger.info(f"Successfully posted {len(self.urls_batch)} URLs to {self.api_url}")
        except requests.RequestException as e:
            spider.logger.error(f"Failed to send URLs to {self.api_url}: {e}")
            raise DropItem(f"POST request failed: {e}")
        finally:
            self.urls_batch.clear()

    def close_spider(self, spider):
        """Finalize operations: close files or send remaining batched URLs."""
        if self.api_url:
            self._send_post_request(spider)
        elif self.current_file:
            self.current_file.close()


class DeDeuplicatorPipeline:
    """Class for pipeline that removes duplicate items"""

    def __init__(self):
        self.urls_seen = set()

    def process_item(self, item, _spider):
        """
        If item has already been seen, drop it otherwise add to
        """
        if item["url"] in self.urls_seen:
            raise DropItem("Item already seen!")

        self.urls_seen.add(item["url"])
        return item
