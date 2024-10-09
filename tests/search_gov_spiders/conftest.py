import json
from pathlib import Path

import pytest


@pytest.fixture(name="crawl_sites_test_file")
def fixture_crawl_sites_test_file() -> Path:
    return Path(__file__).parent / "crawl-sites-test.json"


@pytest.fixture(name="crawl_sites_test_file_json")
def fixture_crawl_sites_test_file_json(crawl_sites_test_file):
    return json.loads(crawl_sites_test_file.resolve().read_text())
