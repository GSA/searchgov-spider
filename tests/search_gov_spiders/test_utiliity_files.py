import json
import plistlib
import sqlite3
import subprocess
import tempfile
from collections import namedtuple
from datetime import datetime
from pathlib import Path
from typing import Self

import pytest
from freezegun import freeze_time

from search_gov_crawler.search_gov_spiders.utility_files.import_plist import (
    apply_manual_updates,
    convert_plist_to_json,
    create_allowed_domain,
)
from search_gov_crawler.search_gov_spiders.utility_files.init_schedule import (
    SpiderSchedule,
    SpiderScheduleSlot,
    get_data_path,
    init_schedule,
    transform_crawl_sites,
    truncate_table,
)

ALLOWED_DOMAIN_TEST_CASES = [
    ("https://www.example.com", "example.com"),
    ("https://example.com", "example.com"),
    ("https://www2.example.com", "example.com"),
    ("https://www7.example.com", "example.com"),
    ("https://www2.example.com/another/page", "example.com"),
]


@pytest.mark.parametrize(("input_url", "expected_result"), ALLOWED_DOMAIN_TEST_CASES)
def test_create_allowed_domain(input_url, expected_result):
    assert create_allowed_domain(input_url) == expected_result


def test_convert_plist_to_json(monkeypatch):
    def mock_read_text(*_args, **_kwargs):
        return "some text"

    def mock_plist_loads(*_args, **_kwargs):
        return [
            {
                "name": "scrape example 1",
                "dateStamp": datetime(2024, 1, 1, 12, 12, 12),
                "startingUrl": "https://www.example.com/1",
                "runJS": True,
                "AnotherField": 100,
                "scheduleCalendarIntervalMatrix": 1,
                "id": "test1",
            },
            {
                "name": "Scrape Example 2",
                "dateStamp": datetime(2024, 2, 1, 12, 12, 12),
                "startingUrl": "https://www.example.com/2",
                "runJS": False,
                "AnotherField": 200,
                "scheduleCalendarIntervalMatrix": 1,
                "id": "test2",
            },
            {
                "name": "Scrape Example - 3",
                "dateStamp": datetime(2024, 3, 1, 12, 12, 12),
                "startingUrl": "https://www.example.com/3",
                "runJS": True,
                "AnotherField": 300,
                "scheduleCalendarIntervalMatrix": 1,
                "id": "test3",
            },
            {
                "name": "Inactive Example",
                "dateStamp": datetime(2024, 3, 1, 12, 12, 12),
                "startingUrl": "https://www.example.com/3",
                "runJS": False,
                "AnotherField": 400,
                "scheduleCalendarIntervalMatrix": 0,
                "id": "test4",
            },
            {
                "name": "Filtered Example",
                "dateStamp": datetime(2024, 3, 1, 12, 12, 12),
                "startingUrl": "https://www.example.com/4",
                "runJS": False,
                "AnotherField": 400,
                "scheduleCalendarIntervalMatrix": 1,
                "id": "20220616-073159",
            },
        ]

    monkeypatch.setattr(Path, "exists", lambda x: True)
    monkeypatch.setattr(plistlib, "loads", mock_plist_loads)

    with tempfile.TemporaryDirectory() as temp_dir:
        monkeypatch.setattr(Path, "parent", Path(temp_dir))

        with monkeypatch.context() as m:
            m.setattr(Path, "read_text", mock_read_text)
            convert_plist_to_json(input_file="input_file.plist", output_file="crawl-sites-sample.json", write_full_output=True)

        crawl_output_records = json.loads(
            Path(temp_dir).joinpath("crawl-sites-sample.json").resolve().read_text(encoding="UTF")
        )
        full_output_records = json.loads(Path(temp_dir).joinpath("input_file.json").resolve().read_text(encoding="UTF"))

        assert len(crawl_output_records) == 3
        assert crawl_output_records[0] == {
            "name": "scrape example 1",
            "allow_query_string": False,
            "allowed_domains": "example.com",
            "handle_javascript": True,
            "schedule": None,
            "output_target": "endpoint",
            "starting_urls": "https://www.example.com/1",
        }
        assert len(full_output_records) == 5
        assert full_output_records[0] == {
            "dateStamp": "2024-01-01T12:12:12",
            "name": "scrape example 1",
            "startingUrl": "https://www.example.com/1",
            "runJS": True,
            "scheduleCalendarIntervalMatrix": 1,
            "AnotherField": 100,
            "id": "test1",
        }


def test_convert_plist_to_json_missing_input_file(monkeypatch):
    non_existant_file = "./this-is-a-missing-file-path.txt"

    def mock_resolve(*_args, **_kwargs) -> Path:
        return Path(non_existant_file)

    monkeypatch.setattr(Path, "resolve", mock_resolve)

    with pytest.raises(FileNotFoundError, match="Input file this-is-a-missing-file-path.txt does not exist!"):
        convert_plist_to_json(input_file=non_existant_file, output_file="crawl-sites-sample.json", write_full_output=True)


MANUAL_UPDATE_TEST_CASES = [
    ("https://www.dantes.mil/", "name", "DOD DANTES"),
    ("https://www.cfm.va.gov/til/", "allowed_domains", "cfm.va.gov/til/"),
    ("https://www.va.gov/accountability/", "allowed_domains", "va.gov/accountability/"),
    ("https://www.va.gov/resources/", "allowed_domains", "va.gov/resources/"),
    ("https://www.herc.research.va.gov/", "allow_query_string", True),
    ("https://www.herc.research.va.gov/", "name", "VA HERC Research"),
]


@pytest.mark.parametrize(("starting_urls", "field", "value"), MANUAL_UPDATE_TEST_CASES)
def test_manual_updates(starting_urls, field, value):
    input_record = {"some_field": "some_value"} | {"starting_urls": starting_urls}
    record = apply_manual_updates(input_record)
    assert record[field] == value


def test_spider_schedule():
    spider_schedule = SpiderSchedule()
    scheduled_slots = [spider_schedule.get_next_slot() for _ in range(47)]
    assert scheduled_slots == [
        SpiderScheduleSlot("mon", "03", "30"),
        SpiderScheduleSlot("mon", "05", "30"),
        SpiderScheduleSlot("mon", "07", "30"),
        SpiderScheduleSlot("mon", "09", "30"),
        SpiderScheduleSlot("mon", "11", "30"),
        SpiderScheduleSlot("mon", "13", "30"),
        SpiderScheduleSlot("mon", "15", "30"),
        SpiderScheduleSlot("mon", "17", "30"),
        SpiderScheduleSlot("mon", "19", "30"),
        SpiderScheduleSlot("mon", "21", "30"),
        SpiderScheduleSlot("tue", "03", "30"),
        SpiderScheduleSlot("tue", "05", "30"),
        SpiderScheduleSlot("tue", "07", "30"),
        SpiderScheduleSlot("tue", "09", "30"),
        SpiderScheduleSlot("tue", "11", "30"),
        SpiderScheduleSlot("tue", "13", "30"),
        SpiderScheduleSlot("tue", "15", "30"),
        SpiderScheduleSlot("tue", "17", "30"),
        SpiderScheduleSlot("tue", "19", "30"),
        SpiderScheduleSlot("tue", "21", "30"),
        SpiderScheduleSlot("wed", "03", "30"),
        SpiderScheduleSlot("wed", "05", "30"),
        SpiderScheduleSlot("wed", "07", "30"),
        SpiderScheduleSlot("wed", "09", "30"),
        SpiderScheduleSlot("wed", "11", "30"),
        SpiderScheduleSlot("wed", "13", "30"),
        SpiderScheduleSlot("wed", "21", "30"),
        SpiderScheduleSlot("thu", "03", "30"),
        SpiderScheduleSlot("thu", "05", "30"),
        SpiderScheduleSlot("thu", "07", "30"),
        SpiderScheduleSlot("thu", "09", "30"),
        SpiderScheduleSlot("thu", "11", "30"),
        SpiderScheduleSlot("thu", "13", "30"),
        SpiderScheduleSlot("thu", "15", "30"),
        SpiderScheduleSlot("thu", "17", "30"),
        SpiderScheduleSlot("thu", "19", "30"),
        SpiderScheduleSlot("thu", "21", "30"),
        SpiderScheduleSlot("fri", "03", "30"),
        SpiderScheduleSlot("fri", "05", "30"),
        SpiderScheduleSlot("fri", "07", "30"),
        SpiderScheduleSlot("fri", "09", "30"),
        SpiderScheduleSlot("fri", "11", "30"),
        SpiderScheduleSlot("fri", "13", "30"),
        SpiderScheduleSlot("fri", "15", "30"),
        SpiderScheduleSlot("fri", "17", "30"),
        SpiderScheduleSlot("fri", "19", "30"),
        SpiderScheduleSlot("fri", "21", "30"),
    ]


def test_spider_schedule_not_implemented():
    spider_schedule = SpiderSchedule()
    with pytest.raises(NotImplementedError, match="This class does not support assignment beyond Fri 21:30"):
        _schedule_slots = [spider_schedule.get_next_slot() for _ in range(48)]


def test_get_data_path(monkeypatch):
    test_dir = "/dev/null"
    monkeypatch.setenv("DATA_PATH", test_dir)
    assert get_data_path() == Path(test_dir)


def test_get_data_path_env_not_set(monkeypatch):
    monkeypatch.delenv("DATA_PATH", raising=False)

    with tempfile.TemporaryDirectory() as temp_dir:
        # setup
        temp_scrapydweb_path = Path(temp_dir) / "bin/scrapydweb"
        temp_scrapydweb_path.mkdir(parents=True, exist_ok=True)
        temp_data_path = Path(temp_dir) / "lib/python3.12/site-packages/scrapydweb/data"
        temp_data_path.mkdir(parents=True, exist_ok=True)

        def mock_run(*_args, **_kwargs):
            MockProcess = namedtuple("MockProcess", "stdout")
            return MockProcess(stdout=str(temp_scrapydweb_path).encode('UTF-8"'))

        monkeypatch.setattr(subprocess, "run", mock_run)
        assert get_data_path() == Path(temp_dir) / "lib/python3.12/site-packages/scrapydweb/data"


@freeze_time("2024-01-01 00:00:00", tz_offset=0)
def test_transform_crawl_sites(crawl_sites_test_file_json):
    transformed_records = transform_crawl_sites(crawl_sites_test_file_json)

    # pylint: disable=line-too-long
    assert transformed_records == [
        {
            "id": 1,
            "name": "Quotes 1",
            "trigger": "cron",
            "create_time": "2024-01-01 00:00:00+00:00",
            "update_time": "2024-01-01 00:00:00+00:00",
            "project": "search_gov_spiders",
            "version": "default: the latest version",
            "spider": "domain_spider",
            "jobid": "quotes-1",
            "settings_arguments": '{"allowed_domains": "quotes.toscrape.com", "setting": [], "start_urls": "https://quotes.toscrape.com/"}',
            "selected_nodes": "[1]",
            "year": "*",
            "month": "*",
            "day": "*",
            "week": "*",
            "day_of_week": "mon",
            "hour": "03",
            "minute": "30",
            "second": "0",
            "start_date": None,
            "end_date": None,
            "timezone": "UTC",
            "jitter": 0,
            "misfire_grace_time": 600,
            "coalesce": "True",
            "max_instances": 1,
        },
        {
            "id": 2,
            "name": "Quotes 2",
            "trigger": "cron",
            "create_time": "2024-01-01 00:00:00+00:00",
            "update_time": "2024-01-01 00:00:00+00:00",
            "project": "search_gov_spiders",
            "version": "default: the latest version",
            "spider": "domain_spider_js",
            "jobid": "quotes-2",
            "settings_arguments": '{"allowed_domains": "quotes.toscrape.com", "setting": [], "start_urls": "https://quotes.toscrape.com/js/"}',
            "selected_nodes": "[1]",
            "year": "*",
            "month": "*",
            "day": "*",
            "week": "*",
            "day_of_week": "mon",
            "hour": "05",
            "minute": "30",
            "second": "0",
            "start_date": None,
            "end_date": None,
            "timezone": "UTC",
            "jitter": 0,
            "misfire_grace_time": 600,
            "coalesce": "True",
            "max_instances": 1,
        },
        {
            "id": 3,
            "name": "Quotes 3",
            "trigger": "cron",
            "create_time": "2024-01-01 00:00:00+00:00",
            "update_time": "2024-01-01 00:00:00+00:00",
            "project": "search_gov_spiders",
            "version": "default: the latest version",
            "spider": "domain_spider_js",
            "jobid": "quotes-3",
            "settings_arguments": '{"allowed_domains": "quotes.toscrape.com", "setting": [], "start_urls": "https://quotes.toscrape.com/js-delayed/"}',
            "selected_nodes": "[1]",
            "year": "*",
            "month": "*",
            "day": "*",
            "week": "*",
            "day_of_week": "mon",
            "hour": "07",
            "minute": "30",
            "second": "0",
            "start_date": None,
            "end_date": None,
            "timezone": "UTC",
            "jitter": 0,
            "misfire_grace_time": 600,
            "coalesce": "True",
            "max_instances": 1,
        },
        {
            "id": 4,
            "name": "Quotes 4",
            "trigger": "cron",
            "create_time": "2024-01-01 00:00:00+00:00",
            "update_time": "2024-01-01 00:00:00+00:00",
            "project": "search_gov_spiders",
            "version": "default: the latest version",
            "spider": "domain_spider",
            "jobid": "quotes-4",
            "settings_arguments": '{"allowed_domains": "quotes.toscrape.com/tag/", "setting": [], "start_urls": "https://quotes.toscrape.com/"}',
            "selected_nodes": "[1]",
            "year": "*",
            "month": "*",
            "day": "*",
            "week": "*",
            "day_of_week": "mon",
            "hour": "09",
            "minute": "30",
            "second": "0",
            "start_date": None,
            "end_date": None,
            "timezone": "UTC",
            "jitter": 0,
            "misfire_grace_time": 600,
            "coalesce": "True",
            "max_instances": 1,
        },
    ]


class MockSqlite3Connection:
    def __init__(self, database: str):
        self.database = database

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args, **kwargs): ...

    @staticmethod
    def execute(*_args, **_kwargs):
        return True

    @staticmethod
    def executemany(*_args, **_kwargs):
        return True

    @staticmethod
    def commit():
        return True


def test_truncate_table(caplog):
    with caplog.at_level("INFO"):
        truncate_table(conn=MockSqlite3Connection("test_database.db"), table_name="some_full_table")  # type: ignore

    assert "Successfully truncated table some_full_table" in caplog.messages


def test_init_schedule(caplog, monkeypatch, crawl_sites_test_file):
    def mock_connect(*_args, **_kwargs):
        return MockSqlite3Connection("test_database.db")

    module_path = "search_gov_crawler.search_gov_spiders.utility_files.init_schedule"
    monkeypatch.setattr(f"{module_path}.transform_crawl_sites", lambda x: [])
    monkeypatch.setattr(f"{module_path}.get_data_path", lambda: Path("/some/test/path"))
    monkeypatch.setattr(f"{module_path}.truncate_table", lambda x, y: True)
    monkeypatch.setattr(sqlite3, "connect", mock_connect)

    with caplog.at_level("INFO"):
        init_schedule(input_file=str(crawl_sites_test_file))

    assert "Inserted 0 records into task table!" in caplog.messages


def test_init_schedule_missing_input_file(monkeypatch):
    non_existant_file = "./this-is-a-missing-file-path.txt"

    def mock_resolve(*_args, **_kwargs) -> Path:
        return Path(non_existant_file)

    monkeypatch.setattr(Path, "resolve", mock_resolve)
    with pytest.raises(FileNotFoundError, match="Input file this-is-a-missing-file-path.txt does not exist!"):
        init_schedule(input_file=non_existant_file)
