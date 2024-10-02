from contextlib import suppress

import pytest
from scrapy.exceptions import DropItem

from search_gov_crawler.search_gov_spiders.items import SearchGovSpidersItem
from search_gov_crawler.search_gov_spiders.pipelines import DeDeuplicatorPipeline


@pytest.mark.parametrize(
    ("items", "urls_seen_length"),
    [
        (
            [
                SearchGovSpidersItem(url="https://www.example.com/1"),
                SearchGovSpidersItem(url="https://www.example.com/2"),
            ],
            2,
        ),
        (
            [
                SearchGovSpidersItem(url="https://www.example.com/1"),
                SearchGovSpidersItem(url="https://www.example.com/1"),
            ],
            1,
        ),
    ],
)
def test_deduplicator_pipeline(items, urls_seen_length):
    pl = DeDeuplicatorPipeline()

    with suppress(DropItem):
        for item in items:
            pl.process_item(item, None)

    assert len(pl.urls_seen) == urls_seen_length
