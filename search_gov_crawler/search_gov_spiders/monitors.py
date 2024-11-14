import os
from pathlib import Path
from spidermon import MonitorSuite
from spidermon.contrib.actions.email.smtp import SendSmtpEmail
from spidermon.contrib.actions.reports.files import CreateFileReport
from spidermon.contrib.scrapy.monitors.monitors import ItemCountMonitor, UnwantedHTTPCodesMonitor, PeriodicItemCountMonitor, PeriodicExecutionTimeMonitor

SPIDERMON_UNWANTED_HTTP_CODES = "SPIDERMON_UNWANTED_HTTP_CODES"
SPIDERMON_UNWANTED_HTTP_CODES_MAX_COUNT = "SPIDERMON_UNWANTED_HTTP_CODES_MAX_COUNT"
SPIDERMON_MAX_EXECUTION_TIME = "SPIDERMON_MAX_EXECUTION_TIME"
SPIDERMON_ITEM_COUNT_INCREASE = "SPIDERMON_ITEM_COUNT_INCREASE"
SPIDERMON_MIN_ITEMS = "SPIDERMON_MIN_ITEMS"

class CreateCustomFileReport(CreateFileReport):
    template_paths = [Path(__file__).parent / "actions"]

class CreateCustomEmailReport(SendSmtpEmail):
    dirname= os.path.dirname(__file__)
    body_html_template = os.path.join(dirname, 'actions', 'results.jinja')

class PeriodicMonitorSuite(MonitorSuite):
    monitors = [
        ItemCountMonitor, UnwantedHTTPCodesMonitor, PeriodicItemCountMonitor, PeriodicExecutionTimeMonitor
    ]

    monitors_failed_actions = [
        CreateCustomFileReport, CreateCustomEmailReport
    ]