from pathlib import Path
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from scrapy.utils.project import get_project_settings
from search_gov_crawler.search_gov_spiders.spiders.armymwr import ArmymwrSpider
from search_gov_crawler.search_gov_spiders.spiders.domain_spider import DomainSpider
from search_gov_crawler.separateOutput import separateOutput
import os

settings_file_path = "search_gov_crawler.search_gov_spiders.pip_settings"
os.environ.setdefault("SCRAPY_SETTINGS_MODULE", settings_file_path)


def hello_world():
    """
    This is meant to be a quick sanity check test method that package was installed correctly.
    """
    print("Hello World")


def run_test_spider():
    """
    This is meant to be a quick check test method that we can run a short spider.
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

    # need to get latest file
    separateOutput("items.json", 1000)


def run_all_domains():
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(DomainSpider)
    process.start()
    # TODO: separateOutput(fileFromSpider, 3900000)
