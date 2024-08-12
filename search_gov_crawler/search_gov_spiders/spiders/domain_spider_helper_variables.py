import os
import sys

PLAYWRIGHT_FLAG = True


# fmt: off
filter_extensions = [
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

ALLOWED_CONTENT_TYPE = [
    "text/html",
    "text/plain",
    "application/msword",
    "application/pdf",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
]

# fmt: on

starting_urls = os.path.join(
    os.path.dirname(sys.modules[__name__].__file__),
    "../utility_files/startingUrls.txt"
)

start_urls_list = []
with open(starting_urls, encoding="utf-8") as file:
    while line := file.readline():
        start_urls_list.append(line.rstrip())

domains = os.path.join(
    os.path.dirname(sys.modules[__name__].__file__),
    "../utility_files/domains.txt"
)

domains_list = []
with open(domains, encoding="utf-8") as file:
    while line := file.readline():
        domains_list.append(line.rstrip())
