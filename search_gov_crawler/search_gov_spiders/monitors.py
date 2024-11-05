import datetime
import json
import copy
from pathlib import Path
from spidermon import Monitor, MonitorSuite, monitors
from spidermon.contrib.monitors.mixins.stats import StatsMonitorMixin
from spidermon.contrib.actions.reports.files import CreateFileReport
from spidermon.contrib.actions.email.smtp import SendSmtpEmail
# from search_gov_spiders.actions import MyCustomEmailAction

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
    template_paths = [Path(__file__).parent / "reports"]

@monitors.name('Item count monitor')
class ItemCountMonitor(Monitor):
    """Check if spider extracted the minimum number of items.

    You can configure it using ``SPIDERMON_MIN_ITEMS`` setting.
    There's **NO** default value for this setting, if you try to use this
    monitor without setting it, it'll raise a ``NotConfigured`` exception.
    """

    @monitors.name('Minimum number of items')
    def test_minimum_number_of_items(self):
        crawler = self.data.get("crawler")

        item_extracted = getattr(
            self.data.stats, 'item_scraped_count', 0)
        minimum_threshold = crawler.settings.getint(SPIDERMON_MIN_ITEMS)

        msg = 'Extracted less than {} items'.format(
            minimum_threshold)
        self.assertTrue(
            item_extracted >= minimum_threshold, msg=msg
        )

@monitors.name('Unwanted HTTP codes monitor')
class UnwantedHTTPCodesMonitor(Monitor):
    """Check for maximum number of unwanted HTTP codes.
    You can configure it using ``SPIDERMON_UNWANTED_HTTP_CODES_MAX_COUNT`` setting
    or ``SPIDERMON_UNWANTED_HTTP_CODES`` setting

    This monitor fails if during the spider execution, we receive
    more than the number of ``SPIDERMON_UNWANTED_HTTP_CODES_MAX_COUNT``
    setting for at least one of the HTTP Status Codes in the list defined in
    ``SPIDERMON_UNWANTED_HTTP_CODES`` setting.

    Default values are:

    .. highlight:: python
    .. code-block:: python

        SPIDERMON_UNWANTED_HTTP_CODES_MAX_COUNT = 10
        SPIDERMON_UNWANTED_HTTP_CODES = [400, 407, 429, 500, 502, 503, 504, 523, 540, 541]

    ``SPIDERMON_UNWANTED_HTTP_CODES`` can also be a dictionary with the HTTP Status Code
    as key and the maximum number of accepted responses with that code.

    With the following setting, the monitor will fail if more than 100 responses are
    404 errors or at least one 500 error:

    .. highlight:: python
    .. code-block:: python

        SPIDERMON_UNWANTED_HTTP_CODES = {
            400: 100,
            500: 0,
        }

    Furthermore, instead of being a numeric value, the code accepts a dictionary which can
    contain any of two keys: ``max_count`` and ``max_percentage``. The former refers to an
    absolute value and works the same way as setting an integer value. The latter refers
    to a max_percentage of the total number of requests the spider made. If both are set, the
    monitor will fail if any of the conditions are met. If none are set, it will default to
    ``DEFAULT_UNWANTED_HTTP_CODES_MAX_COUNT```.

    With the following setting, the monitor will fail if it has at least one 500 error or
    if there are more than ``min(100, 0.5 * total requests)`` 400 responses.

    .. highlight:: python
    .. code-block:: python

        SPIDERMON_UNWANTED_HTTP_CODES = {
            400: {"max_count": 100, "max_percentage": 0.5},
            500: 0,
        }

    """
        
    DEFAULT_UNWANTED_HTTP_CODES_MAX_COUNT = 10
    DEFAULT_UNWANTED_HTTP_CODES = [400, 407, 429, 500, 502, 503, 504, 523, 540, 541]
    

    @monitors.name("Should not hit the limit of unwanted http status")
    def test_check_unwanted_http_codes(self):
        crawler = self.data.get("crawler")
        unwanted_http_codes = getdictorlist(
            crawler,
            SPIDERMON_UNWANTED_HTTP_CODES,
            self.DEFAULT_UNWANTED_HTTP_CODES,
        )

        errors_max_count = crawler.settings.getint(
            SPIDERMON_UNWANTED_HTTP_CODES_MAX_COUNT,
            self.DEFAULT_UNWANTED_HTTP_CODES_MAX_COUNT,
        )

        if not isinstance(unwanted_http_codes, dict):
            unwanted_http_codes = {
                code: errors_max_count for code in unwanted_http_codes
            }

        requests = self.data.stats.get("downloader/request_count", 0)
        for code, max_errors in unwanted_http_codes.items():
            code = int(code)
            count = self.data.stats.get(f"downloader/response_status_count/{code}", 0)

            percentage_trigger = False

            if isinstance(max_errors, dict):
                absolute_max_errors = max_errors.get("max_count")
                percentual_max_errors = max_errors.get("max_percentage")

                # if the user passed an empty dict, use the default count
                if not absolute_max_errors and not percentual_max_errors:
                    max_errors = self.DEFAULT_UNWANTED_HTTP_CODES_MAX_COUNT

                else:
                    # calculate the max errors based on percentage
                    # if there's no percentage set, take the number
                    # of requests as this is the same as disabling the check
                    calculated_percentage_errors = int(
                        percentual_max_errors * requests
                        if percentual_max_errors
                        else requests
                    )

                    # takes the minimum of the two values.
                    # if no absolute max errors were set, take the number
                    # of requests as this effectively disables this check
                    max_errors = min(
                        absolute_max_errors if absolute_max_errors else requests,
                        calculated_percentage_errors,
                    )

                    # if the max errors were defined by the percentage, remember it
                    # so we can properly format the error message.
                    percentage_trigger = max_errors == calculated_percentage_errors

            stat_message = (
                "This exceeds the limit of {} ({}% of {} total requests)".format(
                    max_errors, percentual_max_errors * 100, requests
                )
                if percentage_trigger
                else "This exceeds the limit of {}".format(max_errors)
            )

            msg = (
                "Found {} Responses with status code={} - ".format(count, code)
                + stat_message
            )
            self.assertTrue(count <= max_errors, msg=msg)

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


class SpiderCloseMonitorSuite(MonitorSuite):

    monitors = [
        ItemCountMonitor, 
    ]

    monitors_failed_actions = [
        CreateCustomFileReport
    ]

class PeriodicMonitorSuite(MonitorSuite):
    monitors = [
        UnwantedHTTPCodesMonitor, PeriodicItemCountMonitor, PeriodicExecutionTimeMonitor
    ]

    monitors_failed_actions = [
        CreateCustomFileReport
    ]