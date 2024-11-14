import datetime
import json
import copy
import os
from pathlib import Path
from spidermon import Monitor, MonitorSuite, monitors
from spidermon.contrib.scrapy.monitors.monitors import ItemCountMonitor, UnwantedHTTPCodesMonitor
from spidermon.contrib.monitors.mixins.stats import StatsMonitorMixin
from spidermon.contrib.actions.reports.files import CreateFileReport
from spidermon.contrib.actions.email.smtp import SendSmtpEmail

SPIDERMON_UNWANTED_HTTP_CODES = "SPIDERMON_UNWANTED_HTTP_CODES"
SPIDERMON_UNWANTED_HTTP_CODES_MAX_COUNT = "SPIDERMON_UNWANTED_HTTP_CODES_MAX_COUNT"
SPIDERMON_MAX_EXECUTION_TIME = "SPIDERMON_MAX_EXECUTION_TIME"
SPIDERMON_ITEM_COUNT_INCREASE = "SPIDERMON_ITEM_COUNT_INCREASE"
SPIDERMON_MIN_ITEMS = "SPIDERMON_MIN_ITEMS"

def getdictorlist(crawler, name, default=None):
    value = crawler.settings.get(name, default)
    if value is None:
        return {}
    if isinstance(value, str):
        try:
            return json.loads(value, object_pairs_hook=OrderedDict)
        except ValueError:
            return value.split(",")
    return copy.deepcopy(value)

class CreateCustomFileReport(CreateFileReport):
    template_paths = [Path(__file__).parent / "actions"]

class CreateCustomEmailReport(SendSmtpEmail):
    dirname= os.path.dirname(__file__)
    body_html_template = os.path.join(dirname, 'actions', 'results.jinja')

@monitors.name("Periodic item count increase monitor")
class PeriodicItemCountMonitor(Monitor):
    """Check for increase in item count.

    You can configure the threshold for increase using
    ``SPIDERMON_ITEM_COUNT_INCREASE`` as a project setting or spider attribute.
    Use int value to check for x new items every check or float value to check
    in percentage increase of items.
    """

    @monitors.name('Check SPIDERMON_ITEM_COUNT_INCREASE number of items returned in SPIDERMON_TIME_INTERVAL seconds')
    def test_number_of_items_in_interval(self):
        crawler = self.data.get("crawler")
        item_extracted = getattr(
            self.data.stats, 'item_scraped_count', 0)
        minimum_threshold = crawler.settings.getint(SPIDERMON_ITEM_COUNT_INCREASE)

        msg = 'Extracted less than {} items'.format(
            minimum_threshold)
        self.assertTrue(
            item_extracted >= minimum_threshold, msg=msg
        )

@monitors.name("Periodic execution time monitor")
class PeriodicExecutionTimeMonitor(Monitor, StatsMonitorMixin):
    """Check for runtime exceeding a target maximum runtime.

    You can configure the maximum runtime (in seconds) using
    ``SPIDERMON_MAX_EXECUTION_TIME`` as a project setting or spider attribute."""
        
    # SPIDERMON_MAX_EXECUTION_TIME is how long we want it to be running max whereas SPIDERMON_TIME_INTERVAL in settings.py is how often we check that it's running
    @monitors.name("Maximum execution time reached")
    def test_execution_time(self):
        crawler = self.data.get("crawler")
        max_execution_time = crawler.settings.getint(SPIDERMON_MAX_EXECUTION_TIME)
        if not max_execution_time:
            return

        start_time = self.data.stats.get("start_time")
        if not start_time:
            return

        if start_time.tzinfo:
            now = self.utc_now_with_timezone()
        else:
            now = datetime.datetime.utcnow()

        duration = now - start_time

        msg = "The job has exceeded the maximum execution time"
        self.assertLess(duration.total_seconds(), max_execution_time, msg=msg)

class PeriodicMonitorSuite(MonitorSuite):
    monitors = [
        ItemCountMonitor, UnwantedHTTPCodesMonitor, PeriodicItemCountMonitor, PeriodicExecutionTimeMonitor
    ]

    monitors_failed_actions = [
        CreateCustomFileReport, CreateCustomEmailReport
    ]