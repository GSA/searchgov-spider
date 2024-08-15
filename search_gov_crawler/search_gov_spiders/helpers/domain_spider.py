import re
from pathlib import Path
from typing import Any

PLAYWRIGHT_FLAG = False


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


def is_valid_content_type(content_type_header: Any) -> bool:
    """Check that content type header is in list of allowed values"""

    content_type_header = str(content_type_header)
    for type_regex in ALLOWED_CONTENT_TYPE:
        if re.search(type_regex, content_type_header):
            return True
    return False


def get_default_starting_urls(handle_javascript: bool) -> list[str]:
    """Retrieve list of starting urls from text file"""

    starting_urls_file = Path(__file__).parent.parent / "utility_files" / "startingUrls.txt"
    start_urls_list = starting_urls_file.resolve().read_text().splitlines()
    return start_urls_list


def get_default_allowed_domains(handle_javascript: bool) -> list[str]:
    """Retrieve list of allowed domains from text file"""

    domains_file = Path(__file__).parent.parent / "utility_files" / "domains.txt"
    domains_list = domains_file.resolve().read_text().splitlines()

    return domains_list


def should_abort_request(request) -> bool:
    """Helper function to tell playwright if it should process requests based on resource type"""

    if request.resource_type in FILTER_EXTENSIONS:
        return True
    return False
