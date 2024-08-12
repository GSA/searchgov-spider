# Automatically created by: scrapyd-deploy

from setuptools import setup, find_packages
from scrapyd_api import ScrapydAPI

setup(
    name="search_gov_spiders",
    version="1.0",
    packages=find_packages(),
    entry_points={"scrapy": ["settings = search_gov_spiders.settings"]},
    scrapyd=ScrapydAPI("http://localhost:6800"),
)
