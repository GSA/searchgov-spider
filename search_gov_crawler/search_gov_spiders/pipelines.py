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

    def __init__(self, *_args, **_kwargs):
        self.current_file_size = 0
        self.file_number = 1
        self.parent_file_path = Path(__file__).parent.parent.resolve()
        self.base_path_name = str(self.parent_file_path / f"output/all-links-p{os.getpid()}.csv")
        self.short_file = open(self.base_path_name, "a", encoding="utf-8")
        self.max_file_size = 39000000 #3.9MB max
        self.paginate = True

    def process_item(self, item, _spider):
        """Checks that the file is not at max size.
        Adds it to the file if less, or creates a new file if too large."""
        line = item["url"]
        self.current_file_size += 1
        file_stats = os.stat(self.base_path_name)
        self.current_file_size += file_stats.st_size
        next_file_size = self.current_file_size + len(line)
        if self.paginate and next_file_size > self.max_file_size:
            self.short_file.close()
            new_name = str(self.parent_file_path / f"output/all-links-p{os.getpid()}-{self.file_number}.csv")
            os.rename(self.base_path_name, new_name)
            self.file_number = self.file_number + 1
            self.short_file = open(self.base_path_name, "w", encoding="utf-8")
            self.current_file_size = 0
        self.short_file.write(line)
        self.short_file.write("\n")
        self.current_file_size = self.current_file_size + len(line)
        return item
    
    def _is_batch_too_large(self, new_entry_size):
        pass

    def _is_file_too_large(self, new_entry_size):
        pass

    def _rotate_file(self):
        pass

    def _post_urls(self, spider):
        pass

    def close_spider(self, spider):
        pass

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
