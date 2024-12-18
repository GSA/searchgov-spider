"""
Replacement entrypoint module for logparser to allow for logging in json format. Running logparser as a sub-process
has been disabled in the scrapydweb config file so this module must be run to enable logparser functionality.
The scrapyd-logs directory is specified here. Any other command line settings that would normally be passed to
logparser need to be added here.

Run logparser with the following command: `python -m search_gov_crawler.search_gov_logparser`
"""

import logging

from logparser import run as logparser_run
from logparser.logparser import LogParser
from logparser.utils import custom_settings

from search_gov_crawler.search_gov_spiders.extensions.json_logging import SearchGovSpiderStreamHandler

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(SearchGovSpiderStreamHandler())

custom_settings["scrapyd_logs_dir"] = "scrapyd-logs"
logparser = LogParser(**custom_settings)
logging.getLogger("logparser.logparser").handlers.clear()

logparser_run.main()
