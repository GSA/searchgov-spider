import subprocess

from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.blocking import BlockingScheduler
from search_gov_crawler.scrapy_scheduler import run_scrapy_crawl, transform_crawl_sites, start_scrapy_scheduler


def test_run_scrapy_crawl(caplog, monkeypatch):
    def mock_run(*_args, **_kwargs):
        return True

    monkeypatch.setattr(subprocess, "run", mock_run)
    with caplog.at_level("INFO"):
        run_scrapy_crawl("test_spider", "test-domain.example.com", "http://starting-url.example.com/")

    assert (
        "Successfully completed scrapy crawl with args spider=test_spider, "
        "allowed_domains=test-domain.example.com, start_urls=http://starting-url.example.com/"
    ) in caplog.messages


def test_transform_crawl_sites(crawl_sites_test_file_json):
    transformed_crawl_sites = transform_crawl_sites(crawl_sites_test_file_json)

    # CronTrigger class does not implement __eq__
    triggers = [str(site.pop("trigger")) for site in transformed_crawl_sites]
    assert triggers == [
        str(
            CronTrigger(
                year="*",
                month="*",
                day="*",
                week="*",
                day_of_week="mon",
                hour="03",
                minute="30",
                second=0,
                timezone="UTC",
                jitter=0,
            )
        ),
        str(
            CronTrigger(
                year="*",
                month="*",
                day="*",
                week="*",
                day_of_week="mon",
                hour="05",
                minute="30",
                second=0,
                timezone="UTC",
                jitter=0,
            )
        ),
        str(
            CronTrigger(
                year="*",
                month="*",
                day="*",
                week="*",
                day_of_week="mon",
                hour="07",
                minute="30",
                second=0,
                timezone="UTC",
                jitter=0,
            ),
        ),
        str(
            CronTrigger(
                year="*",
                month="*",
                day="*",
                week="*",
                day_of_week="mon",
                hour="09",
                minute="30",
                second=0,
                timezone="UTC",
                jitter=0,
            ),
        ),
    ]

    assert transformed_crawl_sites == [
        {
            "func": run_scrapy_crawl,
            "id": "quotes-1",
            "name": "Quotes 1",
            "args": ["domain_spider", "quotes.toscrape.com", "https://quotes.toscrape.com/"],
        },
        {
            "func": run_scrapy_crawl,
            "id": "quotes-2",
            "name": "Quotes 2",
            "args": ["domain_spider_js", "quotes.toscrape.com", "https://quotes.toscrape.com/js/"],
        },
        {
            "func": run_scrapy_crawl,
            "id": "quotes-3",
            "name": "Quotes 3",
            "args": ["domain_spider_js", "quotes.toscrape.com", "https://quotes.toscrape.com/js-delayed/"],
        },
        {
            "func": run_scrapy_crawl,
            "id": "quotes-4",
            "name": "Quotes 4",
            "args": ["domain_spider", "quotes.toscrape.com/tag/", "https://quotes.toscrape.com/"],
        },
    ]


def test_start_scrapy_scheduler(caplog, monkeypatch, crawl_sites_test_file):
    monkeypatch.setattr(BlockingScheduler, "start", lambda x: True)

    with caplog.at_level("INFO"):
        start_scrapy_scheduler(input_file=crawl_sites_test_file)

    assert len(caplog.messages) == 4
    assert "Adding job tentatively -- it will be properly scheduled when the scheduler starts" in caplog.messages
