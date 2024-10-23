"""
Replacement entrypoint module for scrapyd to allow for logging in json format.  This entrypoint is specified in the
scrapyd.conf file.  Run scrapyd as normal on the command line.
"""

import sys

from twisted.logger import jsonFileLogObserver, LogLevelFilterPredicate, FilteringLogObserver, LogLevel, ILogObserver
from twisted.web import resource
from scrapyd.app import application
from scrapyd import website


def scrapyd_app(config):
    """Customized app entry point referenced in scrapydconfig that allows for json logging."""

    log_observer = FilteringLogObserver(
        observer=jsonFileLogObserver(sys.stdout),  # type: ignore
        predicates=[
            LogLevelFilterPredicate(LogLevel.info),  # type: ignore
        ],
    )

    app = application(config)
    app.setComponent(ILogObserver, log_observer)

    return app


class DisabledUIRoot(website.Root):
    """
    Customized website root resource that disables existing UI by extending built-in root and
    making the changes we need.
    """

    def __init__(self, config, app):
        super().__init__(config, app)
        print(self.listEntities())
        self.delEntity(b"")
        self.delEntity(b"jobs")
        self.delEntity(b"items")
        self.delEntity(b"logs")
        self.putChild(b"", DisabledUIHome(self))  # type: ignore


class DisabledUIHome(resource.Resource):
    """Replace home resource, i.e. 'http://scrapyd.server.address/' with a empty response."""

    def __init__(self, root):
        super().__init__()
        self.root = root

    def render_GET(self, request):  # pylint: disable=invalid-name
        request.setResponseCode(200)
        return b""
