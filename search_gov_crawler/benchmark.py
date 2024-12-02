import argparse
import logging
import time
import os
from datetime import datetime, UTC, timedelta

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from pythonjsonlogger.json import JsonFormatter

from search_gov_crawler.search_gov_spiders.extensions.json_logging import LOG_FMT
from search_gov_crawler import scrapy_scheduler

logging.basicConfig(level=logging.INFO)
log = logging.getLogger()
log.handlers[0].setFormatter(JsonFormatter(fmt=LOG_FMT))


def benchmark_scrapy(allowed_domains: str, starting_urls: str, handle_javascript: bool, runtime_offset_seconds: int):
    """Function to allow for benchmarking jobs"""

    # Initalize scheduler
    max_workers = min(32, (os.cpu_count() or 1) + 4)  # default from concurrent.futures

    scheduler = BackgroundScheduler(
        jobstores={"memory": MemoryJobStore()},
        executors={"default": ThreadPoolExecutor(max_workers)},
        job_defaults={"coalesce": False, "max_instances": 1},
        timezone="UTC",
    )

    job_name = f"benchmark - {starting_urls}"

    apscheduler_job = {
        "func": scrapy_scheduler.run_scrapy_crawl,
        "id": job_name.lower().replace(" ", "-").replace("---", "-"),
        "name": job_name,
        "next_run_time": datetime.now(tz=UTC) + timedelta(seconds=runtime_offset_seconds),
        "args": [
            "domain_spider" if not handle_javascript else "domain_spider_js",
            allowed_domains,
            starting_urls,
        ],
    }
    scheduler.add_job(**apscheduler_job, jobstore="memory")

    scheduler.start()
    time.sleep(runtime_offset_seconds + 2)
    scheduler.shutdown()  # wait until all jobs are finished


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a scrapy schedule or benchmark based on input.")
    parser.add_argument("-d", "--allowed_domains", type=str, help="domains allowed to crawl", required=True)
    parser.add_argument("-u", "--starting_urls", type=str, help="url used to start crawl", required=True)
    parser.add_argument("-js", "--handle_js", action=argparse.BooleanOptionalAction, help="Flag to enable javascript")
    parser.add_argument("-t", "--runtime_offset", type=int, default=5, help="Number of seconds to offset job start")
    args = parser.parse_args()

    log.info("***RUNNING BENCHMARK TEST***")
    benchmark_args = {
        "allowed_domains": args.allowed_domains,
        "starting_urls": args.starting_urls,
        "handle_javascript": args.handle_js,
        "runtime_offset_seconds": args.runtime_offset,
    }
    benchmark_scrapy(**benchmark_args)
