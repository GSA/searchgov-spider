import datetime
from spidermon import Monitor, MonitorSuite, monitors
from spidermon.contrib.monitors.mixins.stats import StatsMonitorMixin

@monitors.name('Item count Monitor')
class ItemCountMonitor(Monitor):

    @monitors.name('Minimum number of items')
    def test_minimum_number_of_items(self):
        item_extracted = getattr(
            self.data.stats, 'item_scraped_count', 0)
        minimum_threshold = 10

        msg = 'Extracted less than {} items'.format(
            minimum_threshold)
        self.assertTrue(
            item_extracted >= minimum_threshold, msg=msg
        )

@monitors.name('Unwanted HTTP codes')
class UnwantedHTTPCodesMonitor(Monitor):
    UNWANTED_HTTP_CODES_MAX_COUNT = 1
    UNWANTED_HTTP_CODES = [400, 407, 429, 500, 502, 503, 504, 523, 540, 541]

    @monitors.name("Should not hit the limit of unwanted http status")
    def test_check_unwanted_http_codes(self):
        unwanted_http_codes = self.UNWANTED_HTTP_CODES

        errors_max_count = self.UNWANTED_HTTP_CODES_MAX_COUNT

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
                    max_errors = self.UNWANTED_HTTP_CODES_MAX_COUNT

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

@monitors.name("Periodic Item Count Increase Monitor")
class PeriodicItemCountMonitor(Monitor):

    @monitors.name('Check SPIDERMON_ITEM_COUNT_INCREASE number of items returned in SPIDERMON_TIME_INTERVAL seconds')
    def test_number_of_items_in_interval(self):
        item_extracted = getattr(
            self.data.stats, 'item_scraped_count', 0)
        minimum_threshold = 10

        msg = 'Extracted less than {} items'.format(
            minimum_threshold)
        self.assertTrue(
            item_extracted >= minimum_threshold, msg=msg
        )

@monitors.name("Periodic Execution Time Monitor")
class PeriodicExecutionTimeMonitor(Monitor, StatsMonitorMixin):
    # max_execution_time is how long we want it to be running max whereas SPIDERMON_TIME_INTERVAL in settings.py is how often we check that it's running
    @monitors.name("Maximum execution time reached")
    def test_execution_time(self):
        max_execution_time = 1
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

class PeriodicMonitorSuite(MonitorSuite):
    monitors = [
        UnwantedHTTPCodesMonitor, PeriodicItemCountMonitor, PeriodicExecutionTimeMonitor
    ]