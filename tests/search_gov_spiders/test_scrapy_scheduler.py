import subprocess

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from search_gov_crawler.scrapy_scheduler import run_scrapy_crawl, start_scrapy_scheduler, transform_crawl_sites


def test_run_scrapy_crawl(caplog, monkeypatch):
    def mock_run(*_args, **_kwargs):
        return True

    monkeypatch.setattr(subprocess, "run", mock_run)
    with caplog.at_level("INFO"):
        run_scrapy_crawl("test_spider", False, "test-domain.example.com", "http://starting-url.example.com/")

    assert (
        "Successfully completed scrapy crawl with args spider=test_spider, allow_query_string=False, "
        "allowed_domains=test-domain.example.com, start_urls=http://starting-url.example.com/"
    ) in caplog.messages


def test_transform_crawl_sites(crawl_sites_test_file_dataclass):
    transformed_crawl_sites = transform_crawl_sites(crawl_sites_test_file_dataclass)

    # CronTrigger class does not implement __eq__
    triggers = [str(site.pop("trigger")) for site in transformed_crawl_sites]
    for trigger in triggers:
        assert trigger == str(
            CronTrigger(
                month="*",
                day="*",
                day_of_week="*",
                hour="*",
                minute="0,15,30,45",
                timezone="UTC",
            ),
        )

    assert transformed_crawl_sites == [
        {
            "func": run_scrapy_crawl,
            "id": "quotes-1",
            "name": "Quotes 1",
            "args": ["domain_spider", False, "quotes.toscrape.com", "https://quotes.toscrape.com/"],
        },
        {
            "func": run_scrapy_crawl,
            "id": "quotes-2",
            "name": "Quotes 2",
            "args": ["domain_spider_js", False, "quotes.toscrape.com", "https://quotes.toscrape.com/js/"],
        },
        {
            "func": run_scrapy_crawl,
            "id": "quotes-3",
            "name": "Quotes 3",
            "args": ["domain_spider_js", False, "quotes.toscrape.com", "https://quotes.toscrape.com/js-delayed/"],
        },
        {
            "func": run_scrapy_crawl,
            "id": "quotes-4",
            "name": "Quotes 4",
            "args": ["domain_spider", False, "quotes.toscrape.com/tag/", "https://quotes.toscrape.com/"],
        },
    ]


def test_start_scrapy_scheduler(caplog, monkeypatch, crawl_sites_test_file):
    monkeypatch.setattr(BlockingScheduler, "start", lambda x: True)

    with caplog.at_level("INFO"):
        start_scrapy_scheduler(input_file=crawl_sites_test_file)

    assert len(caplog.messages) == 5
    assert "Adding job tentatively -- it will be properly scheduled when the scheduler starts" in caplog.messages
