import pprint

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from urllib.parse import urlparse
import chompjs
import validators

starting_urls = "../utility_files/startingUrls.txt"

start_urls_list = []
with open(starting_urls) as file:
    while line := file.readline():
        start_urls_list.append(line.rstrip())

domains = "../utility_files/domains.txt"

domains_list = []
with open(domains) as file:
    while line := file.readline():
        domains_list.append(line.rstrip())
# for filtering js object elements
unwanted_file_extensions = "../utility_files/unwanted_file_extensions.txt"
unwanted_file_extensions_list = []
with open(unwanted_file_extensions) as file:
    while line := file.readline():
        unwanted_file_extensions_list.append(line.rstrip())


# scrapy command for crawling domain/site
# scrapy crawl domain_spider -a domain=desired_domain -a urls=desired_url
# ex: scrapy crawl domain_spider -a domain=travel.dod.mil -a urls=https://travel.dod.mil


class DomainSpider(CrawlSpider):
    # name = "travelDodMil"
    name = "domain_spider"

    def __init__(self, domain=None, urls=None, *args, **kwargs):
        super(DomainSpider, self).__init__(*args, **kwargs)
        # will grab singular domain
        # multiple comma-separated inputs (ex input: domain=getsmartaboutdrugs.gov,travel.dod.mil)
        # or the list of search.gov domains
        if domain and ',' in domain:
            self.allowed_domains = domain.split(',')
        else:
            self.allowed_domains = [domain] if domain else domains_list
        # urls to start crawling from in domain(s)
        # will grab singular start url
        # multiple comma-separated inputs (ex input: urls=https://getsmartaboutdrugs.gov,https://travel.dod.mil)
        # or the list of search.gov start urls
        if urls and ',' in urls:
            self.start_urls = urls.split(',')
        else:
            self.start_urls = [urls] if urls else start_urls_list

    # file type exclusions
    rules = (
        Rule(
            LinkExtractor(
                allow=(),
                deny=[
                    "calendar",
                    "location-contact",
                    "DTMO-Site-Map/FileId/",
                    # "\*redirect"
                ],
                deny_extensions=[
                    "js",
                    "xml",
                    "gif",
                    "wmv",
                    "wav",
                    "ibooks",
                    "zip",
                    "css",
                    "mp3",
                    "mp4",
                    "cfm",
                    "jpg",
                    "jpeg",
                    "png",
                    "exe",
                    "svg",
                    "ppt",
                    "pptx",
                    "ics",
                    "nc",
                    "tif",
                    "prj",
                    "tar",
                    "tar.gz",
                    "rss",
                    "sfx",
                ],
                unique=True,
            ),
            callback="parse_item",
            follow=True,
        ),
    )

    @staticmethod
    def parse_item(self, response):
        # func won't acknowledge 'response' var coming in when trying to self.log
        # self.logger.info('TEST LOG', response.url)

        # gets js from page
        javascript = response.css("script::text").get()
        data = chompjs.parse_js_object(javascript)
        # loop thru elements and identify valid, in-domain, non-query strings in js object
        # note: some blanks still come thru for some reason
        for element in data:
            if element:
                valid_url = validators.url(element) and str(element)
                if valid_url:
                    query_url = urlparse(element).query
                    url_domain = urlparse(element).netloc
                    is_domain_valid = False
                    for domain in domains_list:
                        if domain in url_domain:
                            is_domain_valid = True

                    has_unwanted_extension = False
                    for ext in unwanted_file_extensions_list:
                        if ext in element:
                            has_unwanted_extension = True

                    pprint.pprint({
                        'VALID URL': valid_url + ', ' + element,
                        'QUERY URL': query_url,
                        'DOMAIN OF URL': url_domain,
                        'URL HAS VALID DOMAIN': is_domain_valid,
                        'URL HAS UNWANTED EXTENSION': has_unwanted_extension
                    })
                    if not query_url and is_domain_valid and not has_unwanted_extension:
                        # yield {
                        #     'JS URL': element,
                        #     # 'NON-QUERY URL:': non_query_url,
                        #     # 'DOMAIN OF URL:': url_domain
                        # }
                        # self.logger.info('JS URL: ', element)
                        yield {'JS URLS': element}
        # normal url grab
        yield {"Link": response.url}
