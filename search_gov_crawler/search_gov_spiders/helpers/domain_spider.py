import json
import re
from pathlib import Path
from typing import Any, Optional

from scrapy.http import Response
from scrapy.linkextractors import LinkExtractor

from search_gov_crawler.search_gov_spiders.items import SearchGovSpidersItem

# fmt: off
FILTER_EXTENSIONS = [
    # archives
    "7z", "7zip", "bz2", "rar", "tar", "tar.gz", "xz", "zip", "gz"
    # images
    "mng", "pct", "bmp", "gif", "jpg", "jpeg", "png", "pst", "psp", "image",
    "tif", "tiff", "ai", "drw", "dxf", "eps", "ps", "svg", "cdr", "ico",
    # audio
    "mp3", "wma", "ogg", "wav", "ra", "aac", "mid", "au", "aiff", "media",
    # video
    "3gp", "asf", "asx", "avi", "mov", "mp4", "mpg", "qt", "rm", "swf",
    "wmv", "m4a", "m4v", "flv", "webm",
    # office suites
    "ppt", "pptx", "pps", "odt", "ods", "odg", "odp",
    # other
    "css", "exe", "bin", "rss", "dmg", "iso", "apk", "js", "xml", "ibooks",
    "cfm", "ics", "nc", "prj", "sfx", "eventsource", "fetch",
    "stylesheet", "websocket", "xhr", "font", "manifest",
]
# fmt: on

ALLOWED_CONTENT_TYPE = [
    "text/html",
    "text/plain",
    "application/msword",
    "application/pdf",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
]


domain_spider_link_extractor = LinkExtractor(
    allow=(),
    deny=[
        "calendar",
        "location-contact",
        "DTMO-Site-Map/FileId/",
        # "\*redirect"
    ],
    deny_extensions=FILTER_EXTENSIONS,
    unique=True,
)


def is_valid_content_type(content_type_header: Any) -> bool:
    """Check that content type header is in list of allowed values"""

    content_type_header = str(content_type_header)
    for type_regex in ALLOWED_CONTENT_TYPE:
        if re.search(type_regex, content_type_header):
            return True
    return False


def parse_item(response: Response):
    """This function is called by spiders to gather the url.
    @url http://quotes.toscrape.com/
    @returns items 1 1
    @scrapes url
    """

    if is_valid_content_type(response.headers.get("content-type", None)):
        yield SearchGovSpidersItem(url=response.url)


def get_crawl_sites(crawl_file_path: Optional[str] = None) -> list[dict]:
    """Read in list of crawl sites from json file"""
    if not crawl_file_path:
        crawl_file = Path(__file__).parent.parent / "utility_files" / "crawl-sites.json"
    else:
        crawl_file = Path(crawl_file_path)

    return json.loads(crawl_file.resolve().read_text())


def default_starting_urls(handle_javascript: bool) -> list[str]:
    """Created default list of starting urls filtered by ability to handle javascript"""

    crawl_sites_records = get_crawl_sites()
    return [
        record["starting_urls"] for record in crawl_sites_records if record["handle_javascript"] is handle_javascript
    ]


def default_allowed_domains(handle_javascript: bool) -> list[str]:
    """Created default list of domains filtered by ability to handle javascript"""

    crawl_sites_records = get_crawl_sites()
    return [
        record["allowed_domains"] for record in crawl_sites_records if record["handle_javascript"] is handle_javascript
    ]
