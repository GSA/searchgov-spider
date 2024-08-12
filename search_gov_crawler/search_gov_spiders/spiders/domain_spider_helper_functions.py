from .domain_spider_helper_variables import (
    filter_extensions,
    PLAYWRIGHT_FLAG,
)


def should_abort_request(request):
    if request.resource_type in filter_extensions:
        return True
    return False


# needed for meta tag for playwright to be added
# note: this seems to work for js rendering but it is resource and time heavy
def set_playwright_true(request, _response):
    if PLAYWRIGHT_FLAG:
        request.meta["playwright"] = True
        request.meta["errback"] = request.errback
    return request
