import io
import json
import logging
import tempfile

import pytest
from scrapy.crawler import Crawler
from scrapy.exceptions import NotConfigured
from scrapy.spiders import Spider
from scrapy.utils.project import get_project_settings

from search_gov_crawler.search_gov_spiders.extensions.json_logging import (
    SearchGovSpiderStreamHandler,
    SearchGovSpiderFileHandler,
    JsonLogging,
)


class SpiderForTest(Spider):
    def __repr__(self):
        return str(
            {"allowed_domains": getattr(self, "allowed_domains"), "name": self.name, "start_urls": self.start_urls}
        )


HANDLER_TEST_CASES = [
    ("This is a test message!!", "This is a test message!!", None, None),
    (
        SpiderForTest(name="handler_test", allowed_domains="example.com", start_urls="https://www.example.com"),
        str({"allowed_domains": "example.com", "name": "handler_test", "start_urls": "https://www.example.com"}),
        SpiderForTest(name="handler_test", allowed_domains="example.com", start_urls="https://www.example.com"),
        {"allowed_domains": "example.com", "name": "handler_test", "start_urls": "https://www.example.com"},
    ),
]


@pytest.mark.parametrize(("input_message", "logged_message", "input_object", "logged_object"), HANDLER_TEST_CASES)
def test_stream_hanlder(input_message, logged_message, input_object, logged_object):
    log_stream = io.StringIO()
    log = logging.getLogger("test_stream_hanlder")
    log.setLevel(logging.INFO)
    log.addHandler(SearchGovSpiderStreamHandler(log_stream))

    log.info(input_message, extra={"scrapy_object": input_object})

    log_message = json.loads(log_stream.getvalue().rstrip("\n"))
    assert list(log_message.keys()) == ["asctime", "name", "levelname", "message", "scrapy_object"]
    assert log_message["message"] == logged_message
    assert log_message["scrapy_object"] == logged_object


@pytest.mark.parametrize(("input_message", "logged_message", "input_object", "logged_object"), HANDLER_TEST_CASES)
def test_file_handler(input_message, logged_message, input_object, logged_object):
    with tempfile.NamedTemporaryFile() as temp_file:
        log = logging.getLogger("test_stream_hanlder")
        log.setLevel(logging.INFO)
        log.addHandler(SearchGovSpiderFileHandler(temp_file.name))

        log.info(input_message, extra={"scrapy_object": input_object})

        log_message = json.load(temp_file)

    assert list(log_message.keys()) == ["asctime", "name", "levelname", "message", "scrapy_object"]
    assert log_message["message"] == logged_message
    assert log_message["scrapy_object"] == logged_object


def test_file_handler_from_handler():
    with tempfile.NamedTemporaryFile() as temp_file:
        spider_file_hanlder = SearchGovSpiderFileHandler.from_hanlder(
            handler=logging.FileHandler(temp_file.name, mode="w", encoding="ASCII", delay=True, errors="test")
        )

        assert spider_file_hanlder.baseFilename == f"{temp_file.name}.json"
        assert spider_file_hanlder.mode == "w"
        assert spider_file_hanlder.encoding == "ASCII"
        assert spider_file_hanlder.delay is True
        assert spider_file_hanlder.errors == "test"


def test_extension_init():
    log = logging.getLogger()
    log.setLevel(logging.INFO)

    extension = JsonLogging()
    assert extension.file_hanlder_enabled is True
    assert any(isinstance(handler, SearchGovSpiderStreamHandler) for handler in log.handlers)


@pytest.fixture(name="project_settings")
def fixture_project_settings(monkeypatch):
    monkeypatch.setenv("SCRAPY_SETTINGS_MODULE", "search_gov_crawler.search_gov_spiders.settings")
    return get_project_settings()


def test_extension_from_crawler_not_configured(project_settings):
    project_settings.set("JSON_LOGGING_ENABLED", False)

    with pytest.raises(NotConfigured, match="JsonLogging Extension is listed in Extension but is not enabled."):
        JsonLogging.from_crawler(Crawler(spidercls=Spider, settings=project_settings))


def test_extension_from_crawler(project_settings):
    extension = JsonLogging.from_crawler(Crawler(spidercls=Spider, settings=project_settings))
    assert isinstance(extension, JsonLogging)


def test_extension_spider_opened(caplog):
    log = logging.getLogger("test_spider")
    log.setLevel(logging.INFO)

    spider = Spider(name="test_spider", allowed_domains=["domain 1", "domain 2"], start_urls=["url 1", "url 2"])
    extension = JsonLogging()
    with caplog.at_level(logging.INFO):
        extension.spider_opened(spider)

    assert (
        "Starting spider test_spider with following args: allowed_domains=domain 1,domain 2 start_urls=url 1,url 2"
        in caplog.messages
    )
