""" Init file to package project for EC2"""

import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from search_gov_crawler.search_gov_spiders.spiders.armymwr import ArmymwrSpider
from search_gov_crawler.search_gov_spiders.spiders.domain_spider \
    import DomainSpider

SETTINGS_FILE_PATH = "search_gov_crawler.search_gov_spiders.pip_settings"
os.environ.setdefault("SCRAPY_SETTINGS_MODULE", SETTINGS_FILE_PATH)


def hello_world():
    """
    This is meant to be a quick sanity check to
    test that package was installed correctly.
    """
    print("Hello World")


def run_test_spider():
    """
    This is meant to be a quick check test method
    that we can run a short spider.
    """
    process = CrawlerProcess(
        settings={
            "FEEDS": {
                "items.json": {"format": "json"},
            },
        }
    )
    process.crawl(ArmymwrSpider)
    process.start()


def run_all_domains():
    """Test that domain spider is working."""
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(DomainSpider)
    process.start()
