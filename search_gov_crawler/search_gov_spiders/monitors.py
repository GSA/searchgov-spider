import os
from pathlib import Path
from spidermon import MonitorSuite
from spidermon.contrib.actions.email.smtp import SendSmtpEmail
from spidermon.contrib.actions.reports.files import CreateFileReport
from spidermon.contrib.scrapy.monitors.monitors import ItemCountMonitor, UnwantedHTTPCodesMonitor, PeriodicItemCountMonitor, PeriodicExecutionTimeMonitor

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