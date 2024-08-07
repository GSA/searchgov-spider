from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Response
import os
import sys
import re
from ..items import SearchGovSpidersItem

IGNORED_EXTENSIONS = [
    # archives
    "7z", "7zip", "bz2", "rar", "tar", "tar.gz", "xz", "zip", "gz"
    # images
    "mng", "pct", "bmp", "gif", "jpg", "jpeg", "png", "pst", "psp",
    "tif", "tiff", "ai", "drw", "dxf", "eps", "ps", "svg", "cdr", "ico",
    # audio
    "mp3", "wma", "ogg", "wav", "ra", "aac", "mid", "au", "aiff",
    # video
    "3gp", "asf", "asx", "avi", "mov", "mp4", "mpg", "qt", "rm", "swf",
    "wmv", "m4a", "m4v", "flv", "webm",
    # office suites
    "ppt", "pptx", "pps", "odt", "ods", "odg", "odp",
    # other
    "css", "exe", "bin", "rss", "dmg", "iso", "apk", "js", "xml", "ibooks",
    "cfm", "ics", "nc", "prj", "sfx",
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


def valid_content_type(type_whitelist, content_type_header):
    content_type_header = str(content_type_header)
    for type_regex in type_whitelist:
        if re.search(type_regex, content_type_header):
            return True
    return False


starting_urls = os.path.join(
    os.path.dirname(sys.modules[__name__].__file__),
    "../utility_files/startingUrls.txt"
)

start_urls_list = []
with open(starting_urls) as file:
    while line := file.readline():
        start_urls_list.append(line.rstrip())

domains = os.path.join(
    os.path.dirname(sys.modules[__name__].__file__),
    "../utility_files/domains.txt"
)

domains_list = []
with open(domains) as file:
    while line := file.readline():
        domains_list.append(line.rstrip())


# scrapy command for crawling domain/site
# scrapy crawl domain_spider -a domain=desired_domain -a urls=desired_url
# ex: ... -a domain=travel.dod.mil -a urls=https://travel.dod.mil


class DomainSpider(CrawlSpider):
    name = "domain_spider"

    def __init__(self, domain: str = None, urls: str = None, *args, **kwargs):
        super(DomainSpider, self).__init__(*args, **kwargs)
        # will grab singular domain
        # multiple comma-separated inputs:
        #   ex: domain=getsmartaboutdrugs.gov,travel.dod.mil
        # or the list of search.gov domains
        self.allowed_domains = domain.split(",") if domain else domains_list
        # urls to start crawling from in domain(s)
        # will grab singular start url
        # multiple comma-separated inputs:
        #   ex: urls=https://getsmartaboutdrugs.gov,https://travel.dod.mil
        # or the list of search.gov start urls
        self.start_urls = urls.split(",") if urls else start_urls_list
        self.url_map = {}

    # file type exclusions
    rules = (
        Rule(
            LinkExtractor(
                allow=(),
                deny=[
                    "calendar",
                    "location-contact",
                    "DTMO-Site-Map/FileId/",
                ],
                deny_extensions=IGNORED_EXTENSIONS,
                unique=True,
            ),
            callback="parse_item",
            follow=True,
        ),
    )

    def parse_item(self, response: Response):
        """This function gathers the url and the status."""
        content_type = response.headers.get("content-type", None)
        if valid_content_type(ALLOWED_CONTENT_TYPE, content_type) and \
                response.url not in self.url_map:
            self.url_map[response.url] = True
            items = SearchGovSpidersItem()
            items["url"] = response.url
            yield items
