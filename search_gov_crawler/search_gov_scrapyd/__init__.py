"""
Replacement entrypoint module for scrapyd to allow for logging in json format.  This entrypoint is specified in the
scrapyd.conf file.  Run scrapyd as normal on the command line.
"""

import sys

from twisted.logger import jsonFileLogObserver, LogLevelFilterPredicate, FilteringLogObserver, LogLevel, ILogObserver

from scrapyd.app import application


def scrapyd_app(config):
    log_observer = FilteringLogObserver(
        observer=jsonFileLogObserver(sys.stdout),
        predicates=[
            LogLevelFilterPredicate(LogLevel.info),
        ],
    )

    app = application(config)
    app.setComponent(ILogObserver, log_observer)

    return app
