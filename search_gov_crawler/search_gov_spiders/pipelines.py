"""Define your item pipelines here
Don't forget to add your pipeline to the ITEM_PIPELINES setting
See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
"""
import requests
import os
from pathlib import Path
from scrapy.exceptions import DropItem

class SearchGovSpidersPipeline:
    """
    Class for pipeline that takes items and adds them
    to output file with a max size of 3.9MB
    """

    MAX_FILE_SIZE_MB = 3.9  # max size in MB
    MAX_FILE_SIZE_BYTES = int(MAX_FILE_SIZE_MB * 1024 * 1024)  # convert to bytes

    def __init__(self, *_args, **_kwargs):
        self.api_url = os.environ.get("SPIDER_URLS_API")
        if not self.api_url:
            self.current_file_size = 0
            self.file_number = 1
            self.parent_file_path = Path(__file__).parent.parent.resolve()
            self.base_path_name = str(self.parent_file_path / f"output/all-links-p{os.getpid()}.csv")
            self.short_file = open(self.base_path_name, "a", encoding="utf-8")
            self.max_file_size = 39000000 #3.9MB max
            self.paginate = True
        else:
            self.urls_batch = []

    def process_item(self, item, _spider):
        """Checks that the file is not at max size.
        Adds it to the file if less, or creates a new file if too large."""

        line = item["url"]
        line_size = len(line.encode("utf-8"))
        
        # If API URL is set, batch URLs and send a POST request when max size is reached
        if self.api_url:
            self.urls_batch.append(item.get("url", ""))
            if self._is_batch_too_large(line_size):
                self._post_urls(spider)
        # Otherwise, write to file
        else:
            self._write_to_file(line)
            
        return item
    
    def _write_to_file(self, line):
        updatd_file_size = self._get_file_size(line)
        if self.paginate and updatd_file_size > self.max_file_size:
           self._create_new_file()
        self.short_file.write(line)
        self.short_file.write("\n")
        self.current_file_size = self.current_file_size + len(line)

    def _get_file_size(self, line):
        self.current_file_size += 1
        file_stats = os.stat(self.base_path_name)
        self.current_file_size += file_stats.st_size
        next_file_size = self.current_file_size + len(line)
        return next_file_size

    def _create_new_file(self):
        self.short_file.close()
        new_name = str(self.parent_file_path / f"output/all-links-p{os.getpid()}-{self.file_number}.csv")
        os.rename(self.base_path_name, new_name)
        self.file_number = self.file_number + 1
        self.short_file = open(self.base_path_name, "w", encoding="utf-8")
        self.current_file_size = 0
    
    def _is_batch_too_large(self, new_entry_size):
        current_batch_size = sum(len(url.encode("utf-8")) for url in self.urls_batch)
        return (current_batch_size + new_entry_size) > self.MAX_FILE_SIZE_BYTES

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

    def close_spider(self, spider):
        """Close the file or send remaining URLs if needed when the spider finishes."""
        if not self.api_url and self.current_file:
            self.short_file.close()
        elif self.api_url:
            self._post_urls(spider)  # Send any remaining URLs on spider close

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
