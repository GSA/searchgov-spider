import unittest

import search_gov_crawler


class TestDomainSpider(unittest.TestCase):
    def test_import_settings(self):
        """
        Test that it can import the settings
        """
        search_gov_crawler.run_all_domains()


if __name__ == "__main__":
    unittest.main()
