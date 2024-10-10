import logging
from typing import Self

from pythonjsonlogger.json import JsonFormatter
from scrapy.spiders import Spider
from scrapy.crawler import Crawler
from scrapy.exceptions import NotConfigured
from scrapy.signals import spider_opened


LOG_FMT = "%(asctime)%(name)%(levelname)%(message)"


def search_gov_default(obj) -> str | None:
    """Function to help serialize scrapy objects"""
    if isinstance(obj, Spider):
        return obj.name

    if isinstance(obj, Crawler):
        return str(obj.settings.get("BOT_NAME", "Unknown"))

    return None


class SearchGovSpiderStreamHandler(logging.StreamHandler):
    """Extension of logging.StreamHandler with our level, fmt, and defaults"""

    def __init__(self, *_args, **_kwargs):
        super().__init__(*_args, **_kwargs)
        formatter = JsonFormatter(fmt=LOG_FMT, json_default=search_gov_default)
        self.setLevel(logging.INFO)
        self.setFormatter(formatter)


class SearchGovSpiderFileHandler(logging.FileHandler):
    """Extension of logging.File with our level, fmt, and defaults"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        formatter = JsonFormatter(fmt=LOG_FMT, json_default=search_gov_default)
        self.setLevel(logging.INFO)
        self.setFormatter(formatter)

    @classmethod
    def from_hanlder(cls, handler: logging.FileHandler) -> "SearchGovSpiderFileHandler":
        """Create a json file handler based on values used by an existing FileHandler"""

        if handler.baseFilename == "/dev/null":
            new_filename = handler.baseFilename
        else:
            new_filename = f"{handler.baseFilename}.json"

        return cls(
            filename=new_filename,
            mode=handler.mode,
            encoding=handler.encoding,
            delay=handler.delay,
            errors=handler.errors,
        )


class JsonLogging:
    """Scrapy extension that injects JSON logging into a spider run."""

    file_hanlder_enabled: bool

    def __init__(self):
        self.file_hanlder_enabled = False
        self._add_json_handlers()

    def _add_json_handlers(self) -> None:
        """Try to add json hanlders for file and streaming"""

        if not self.file_hanlder_enabled:
            root_logger = logging.getLogger()
            root_logger.setLevel(logging.INFO)

            file_handlers = [handler for handler in root_logger.handlers if isinstance(handler, logging.FileHandler)]

            for file_handler in file_handlers:
                root_logger.addHandler(SearchGovSpiderFileHandler.from_hanlder(file_handler))
                self.file_hanlder_enabled = True

            if not any(
                handler for handler in root_logger.handlers if isinstance(handler, SearchGovSpiderStreamHandler)
            ):
                root_logger.addHandler(SearchGovSpiderStreamHandler())

    @classmethod
    def from_crawler(cls, crawler) -> Self:
        """
        Required extension method that checks for configuration and connects extension methons to signals
        """
        if not crawler.settings.getbool("JSON_LOGGING_ENABLED"):
            raise NotConfigured("JsonLogging Extension is listed in Extension but is not enabled.")

        ext = cls()
        crawler.signals.connect(ext.spider_opened, signal=spider_opened)
        return ext

    def spider_opened(self, spider: Spider) -> None:
        """Try to add hanlders and then log arguments passed to the spider"""

        self._add_json_handlers()
        spider_log = logging.getLogger(spider.name)

        spider_log.info(
            "Starting spider %s with following args: allowed_domains=%s start_urls=%s",
            spider.name,
            ",".join(getattr(spider, "allowed_domains", [])),
            ",".join(spider.start_urls),
        )
