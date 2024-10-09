import json
import plistlib
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from search_gov_crawler.search_gov_spiders.utility_files.import_plist import (
    apply_manual_updates,
    convert_plist_to_json,
    create_allowed_domain,
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
            convert_plist_to_json(input_file="input_file.plist", output_file="crawl-sites.json", write_full_output=True)

        crawl_output_records = json.loads(
            Path(temp_dir).joinpath("crawl-sites.json").resolve().read_text(encoding="UTF")
        )
        full_output_records = json.loads(Path(temp_dir).joinpath("input_file.json").resolve().read_text(encoding="UTF"))

        assert len(crawl_output_records) == 3
        assert crawl_output_records[0] == {
            "name": "scrape example 1",
            "job_id": "scrape-example-1",
            "allowed_domains": "example.com",
            "handle_javascript": True,
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


MANUAL_UPDATE_TEST_CASES = [
    ("https://www.dantes.mil/", "name", "DOD DANTES"),
    ("https://www.cfm.va.gov/til/", "allowed_domains", "cfm.va.gov/til/"),
    ("https://www.va.gov/accountability/", "allowed_domains", "va.gov/accountability/"),
    ("https://www.va.gov/resources/", "allowed_domains", "va.gov/resources/"),
]


@pytest.mark.parametrize(("starting_urls", "field", "value"), MANUAL_UPDATE_TEST_CASES)
def test_manual_updates(starting_urls, field, value):
    input_record = {"some_field": "some_value"} | {"starting_urls": starting_urls}
    record = apply_manual_updates(input_record)
    assert record[field] == value
