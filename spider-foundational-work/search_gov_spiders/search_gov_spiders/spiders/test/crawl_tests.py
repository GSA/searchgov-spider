from unittest.case import TestCase

from domain_spider import DomainSpider
from mocks.mock_response import return_response


class SpiderCrawlTest(TestCase):
    def setUp(self):
        self.spider = DomainSpider()

    # tests spider crawl capabilities and parsing func in spider class
    def test_parse(self):
        response = return_response('mock_page.html', None)
        item = self.spider.parse_item(response)
        # convert to list from generative object for assertion
        list_item = list(item)
        self.assertEqual(list_item[0], {'Status': 200, 'Link': 'http://www.example.com'})
