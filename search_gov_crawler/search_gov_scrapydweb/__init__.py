"""
Replacement entrypoint module for scrapydweb to allow for logging in json format. Since scrapydweb does
not allow configuring the modules that start various processes we must use our own entrypoint to enable
json logging.  This entrypoint expects no command line arguments.  If some are needed this module will need
to be modified to accept and apply them.

Run scrapydweb with the following command: `python -m search_gov_crawler.search_gov_scrapydweb`
"""

import logging

from scrapydweb import run as scrapydweb_run

from search_gov_crawler.search_gov_spiders.extensions.json_logging import SearchGovSpiderStreamHandler

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.handlers.clear()
root_logger.addHandler(SearchGovSpiderStreamHandler())


scrapydweb_run.main()
