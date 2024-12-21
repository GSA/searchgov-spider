# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import re
import warnings
from typing import Self
from urllib.parse import urlparse

from scrapy import signals
from scrapy.crawler import Crawler
from scrapy.downloadermiddlewares.offsite import OffsiteMiddleware
from scrapy.exceptions import IgnoreRequest
from scrapy.spiders import Spider
from scrapy.utils.httpobj import urlparse_cached


class MiddlewareBase:
    """Base middleware class that spider middlewares extend"""

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> Self:
        """This method is used by Scrapy to create your spiders."""

        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def spider_opened(self, spider):  # pylint: disable=unused-argument
        """Required method in Middleware.  Called when spider starts."""


class SearchGovSpidersSpiderMiddleware(MiddlewareBase):
    """
    Custom search gov spider middleare.  Not all methods need to be defined. If a method is not defined,
    scrapy acts as if the spider middleware does not modify the passed objects.
    """

    # pylint: disable=unused-argument
    # disable unused arguments in this scrapy-generated class template

    def process_spider_input(self, response, spider):
        """
        Called for each response that goes through the spider middleware and into the spider.

        Should return None or raise an exception.
        """
        return

    def process_spider_output(self, response, result, spider):
        """Called with the results returned from the Spider, after it has processed the response.

        Must return an iterable of Request, or item objects.
        """
        yield from result

    def process_spider_exception(self, response, exception, spider):
        """Called when a spider or process_spider_input() method
        (from other spider middleware) raises an exception.

        Should return either None or an iterable of Request or item objects.
        """
        return

    def process_start_requests(self, start_requests, spider):
        """
        Called with the start requests of the spider, and works similarly to the
        process_spider_output() method, except that it doesn’t have a response associated.

        Must return only requests (not items).
        """
        yield from start_requests


class SearchGovSpidersDownloaderMiddleware(MiddlewareBase):
    """
    Custom search gov spider downloader middleare.  Not all methods need to be defined. If
    a method is not defined, scrapy acts as if the downloader middleware does not modify
    the passed objects.
    """

    # pylint: disable=unused-argument
    # disable unused arguments in this scrapy-generated class template
    def process_request(self, request, spider):
        """
        Called for each request that goes through the downloader middleware.  Ignore
        requests that contain query params except if the spider specifically allows it.

        Must either:
          - return None: continue processing this request
          - or return a Response object
          - or return a Request object
          - or raise IgnoreRequest: process_exception() methods of installed
            downloader middleware will be called
        """

        if spider.allow_query_string:
            return

        if urlparse(request.url).query:
            raise IgnoreRequest

    def process_response(self, request, response, spider):
        """
        Called with the response returned from the downloader.

        Must either;
          - return a Response object
          - return a Request object
          - or raise IgnoreRequest
        """
        return response

    def process_exception(self, request, exception, spider):
        """
        Called when a download handler or a process_request() (from other downloader middleware)
        raises an exception.

        Must either:
          - return None: continue processing this exception
          - return a Response object: stops process_exception() chain
          - return a Request object: stops process_exception() chain
        """
        return


class SearchGovSpidersOffsiteMiddleware(OffsiteMiddleware):
    """Extend OffsiteMiddleware to enable filtering of paths as well as domains"""

    host_regex: re.Pattern
    host_path_regex: re.Pattern

    def spider_opened(self, spider):
        """Overridden to add assignment of host_path_regex"""
        self.host_regex = self.get_host_regex(spider)
        self.host_path_regex = self.get_host_path_regex(spider)

    def should_follow(self, request, spider) -> bool:
        """Overridden to add boolean condition on matching path regex"""
        # hostname can be None for wrong urls (like javascript links)
        cahched_request = urlparse_cached(request)
        host = cahched_request.hostname or ""

        return bool(self.host_regex.search(host) and self.host_path_regex.search(cahched_request.geturl()))

    def get_host_path_regex(self, spider: Spider) -> re.Pattern:
        """New method, modified from 'get_host_regex' method to return path related regex"""
        allowed_domain_paths = getattr(spider, "allowed_domain_paths", None)
        if not allowed_domain_paths:
            return re.compile("")  # allow all by default
        url_pattern = re.compile(r"^https?://.*$")
        port_pattern = re.compile(r":\d+$")
        domains = []

        for domain in allowed_domain_paths:
            if domain is None:
                continue
            if url_pattern.match(domain):
                message = (
                    "allowed_domain_paths accepts only domains, not URLs. "
                    f"Ignoring URL entry {domain} in allowed_domain_paths."
                )
                warnings.warn(message)
            elif port_pattern.search(domain):
                message = (
                    "allowed_domain_paths accepts only domains without ports. "
                    f"Ignoring entry {domain} in allowed_domain_paths."
                )
                warnings.warn(message)
            else:
                domains.append(re.escape(domain))
        regex = rf'{"|".join(domains)}'
        return re.compile(regex)
