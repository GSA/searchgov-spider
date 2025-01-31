"""Define your item pipelines here
Don't forget to add your pipeline to the ITEM_PIPELINES setting
See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
"""

import os
from pathlib import Path

import requests
from scrapy.exceptions import DropItem
from scrapy.spiders import Spider

from search_gov_crawler.search_gov_spiders.items import SearchGovSpidersItem

from search_gov_crawler.elasticsearch.es_batch_upload import SearchGovElasticsearch

SPIDER_INDEX_TO_ELASTICSEARCH = os.environ.get("SPIDER_INDEX_TO_ELASTICSEARCH", True)

class SearchGovSpidersPipeline:
    """
    Pipeline that writes items to files for manual upload, or sends batched POST
    requests (both rotated at ~100KB) to SPIDER_URLS_API if the environment variable is set.
    """

    MAX_URL_BATCH_SIZE_BYTES = int(100 * 1024)  # 100KB in bytes
    APP_PID = os.getpid()

    def __init__(self):
        self.api_url = os.environ.get("SPIDER_URLS_API")
        self.urls_batch = []
        self.file_number = 1
        self.file_path = None
        self.current_file = None
        self.es = SearchGovElasticsearch()

        if not self.api_url:
            output_dir = Path(__file__).parent.parent / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            base_filename = f"all-links-p{self.APP_PID}"
            self.file_path = output_dir / f"{base_filename}.csv"
            self.current_file = open(self.file_path, "a", encoding="utf-8")

    def process_item(self, item: SearchGovSpidersItem, spider: Spider) -> SearchGovSpidersItem:
        """Handle each item by writing to file or batching URLs for an API POST."""
        url = item.get("url", None)
        html_content = item.get("html_content", None)

        if not url or not html_content:
            raise DropItem("Missing URL or HTML in item")
        
        if SPIDER_INDEX_TO_ELASTICSEARCH:
            self.es.add_to_batch(html_content=html_content, url=url, domain_name=spider.name, spider=spider)
        else:
            if self.api_url:
                self._process_api_item(url, spider)
            else:
                self._process_file_item(url)

        return item

    def _process_api_item(self, url: str, spider: Spider) -> None:
        """Batch URLs for API and send POST if size limit is reached."""
        self.urls_batch.append(url)
        if self._batch_size() >= self.MAX_URL_BATCH_SIZE_BYTES:
            self._send_post_request(spider)

    def _process_file_item(self, url: str) -> None:
        """Write URL to file and rotate the file if size exceeds the limit."""
        self.current_file.write(f"{url}\n")
        if self._file_size() >= self.MAX_URL_BATCH_SIZE_BYTES:
            self._rotate_file()

    def _batch_size(self) -> int:
        """Calculate total size of the batched URLs."""
        return sum(len(url.encode("utf-8")) for url in self.urls_batch)

    def _file_size(self) -> int:
        """Get the current file size."""
        self.current_file.flush()  # Ensure the OS writes buffered data to disk
        return self.file_path.stat().st_size

    def _rotate_file(self) -> None:
        """Close the current file, rename it, and open a new one."""
        self.current_file.close()
        rotated_file = self.file_path.with_name(f"{self.file_path.stem}-{self.file_number}.csv")
        os.rename(self.file_path, rotated_file)
        self.current_file = open(self.file_path, "a", encoding="utf-8")
        self.file_number += 1

    def _send_post_request(self, spider: Spider) -> None:
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

    def close_spider(self, spider: Spider) -> None:
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
