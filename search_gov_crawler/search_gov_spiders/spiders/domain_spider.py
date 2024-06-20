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
            # print('--ALLOWED DOMAINS--')
            # pprint.pprint(self.allowed_domains)
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
    def parse_item(response):
        # it's not respecting allowed_domains for some reason??
        # need a fucking regex for the js object fml

        # Js: {object} < -- regex

        # regex needs to filter out non-domain sites

        javascript = response.css("script::text").get()
        data = chompjs.parse_js_object(javascript)
        for element in data:
            if element:
                valid_url = validators.url(element)
                if valid_url:
                    print('VALID URL: ', valid_url)
                    non_query_url = urlparse(element).query
                    url_domain = urlparse(element).netloc

                    print('NON-QUERY URL: ', non_query_url)
                    print('DOMAIN OF URL: ', url_domain)

            #     yield {
            #         'VALID URL': valid_url,
            #         'NON-QUERY URL': non_query_url,
            #         'DOMAIN OF URL': url_domain
            #     }

            if element and validators.url(element):
                # print('VALID JS URL: ' + element)
                yield {'JS URL: ': element}

        # yield {'NON-JS URL: ': response.url}
        # print('NEW OBJECT:')
        # pprint.pprint(data)

        # yield {"JS": data}

        # yield {"Link": response.url}
