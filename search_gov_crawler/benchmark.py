import argparse
import json
import logging
import time
import os
import sys
from datetime import datetime, UTC, timedelta
from pathlib import Path

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from pythonjsonlogger.json import JsonFormatter

from search_gov_crawler.search_gov_spiders.extensions.json_logging import LOG_FMT
from search_gov_crawler import scrapy_scheduler

logging.basicConfig(level=logging.INFO)
log = logging.getLogger()
log.handlers[0].setFormatter(JsonFormatter(fmt=LOG_FMT))


def init_scheduler() -> BackgroundScheduler:
    """Create and return instance of scheduler"""

    max_workers = min(32, (os.cpu_count() or 1) + 4)  # default from concurrent.futures

    return BackgroundScheduler(
        jobstores={"memory": MemoryJobStore()},
        executors={"default": ThreadPoolExecutor(max_workers)},
        job_defaults={"coalesce": False, "max_instances": 1},
        timezone="UTC",
    )


def create_apscheduler_job(
    allowed_domains: str, starting_urls: str, handle_javascript: bool, runtime_offset_seconds: int
) -> dict:
    """Creates job record in format needed by apscheduler"""

    job_name = f"benchmark - {starting_urls}"

    return {
        "func": scrapy_scheduler.run_scrapy_crawl,
        "id": job_name,
        "name": job_name,
        "next_run_time": datetime.now(tz=UTC) + timedelta(seconds=runtime_offset_seconds),
        "args": [
            "domain_spider" if not handle_javascript else "domain_spider_js",
            allowed_domains,
            starting_urls,
        ],
    }


def benchmark_from_file(input_file: Path):
    """Run a benchmark process using input from a file"""

    if not input_file.exists():
        raise FileNotFoundError(f"Input file {input_file} does not exist!")

    crawl_sites = json.loads(input_file.read_text(encoding="UTF-8"))
    max_offset = 0

    scheduler = init_scheduler()
    for crawl_site in crawl_sites:
        apscheduler_job = create_apscheduler_job(**crawl_site)
        scheduler.add_job(**apscheduler_job, jobstore="memory")
        max_offset = max(max_offset, crawl_site["runtime_offset_seconds"])

    scheduler.start()
    time.sleep(max_offset + 2)
    scheduler.shutdown()  # wait until all jobs are finished


def benchmark_from_args(allowed_domains: str, starting_urls: str, handle_javascript: bool, runtime_offset_seconds: int):
    """Run an individual benchmarking job based on args"""

    log.info(
        "Starting benchmark from args! allowed_domains=%s starting_urls=%s handle_javascript=%s runtime_offset_seconds=%s",
        allowed_domains,
        starting_urls,
        handle_javascript,
        runtime_offset_seconds,
    )

    apscheduler_job_kwargs = {
        "allowed_domains": allowed_domains,
        "starting_urls": starting_urls,
        "handle_javascript": handle_javascript,
        "runtime_offset_seconds": runtime_offset_seconds,
    }

    scheduler = init_scheduler()
    apscheduler_job = create_apscheduler_job(**apscheduler_job_kwargs)
    scheduler.add_job(**apscheduler_job, jobstore="memory")

    scheduler.start()
    time.sleep(runtime_offset_seconds + 2)
    scheduler.shutdown()  # wait until all jobs are finished


if __name__ == "__main__":
    no_input_arg = all(arg not in sys.argv for arg in ["-f", "--input_file"])

    parser = argparse.ArgumentParser(description="Run a scrapy schedule or benchmark based on input.")
    parser.add_argument("-f", "--input_file", type=str, help="Path to file containing list of domains to schedule")
    parser.add_argument("-d", "--allowed_domains", type=str, help="domains allowed to crawl", required=no_input_arg)
    parser.add_argument("-u", "--starting_urls", type=str, help="url used to start crawl", required=no_input_arg)
    parser.add_argument(
        "-js", "--handle_js", action=argparse.BooleanOptionalAction, default=False, help="Flag to enable javascript"
    )
    parser.add_argument("-t", "--runtime_offset", type=int, default=5, help="Number of seconds to offset job start")
    args = parser.parse_args()

    if no_input_arg:
        benchmark_args = {
            "allowed_domains": args.allowed_domains,
            "starting_urls": args.starting_urls,
            "handle_javascript": args.handle_js,
            "runtime_offset_seconds": args.runtime_offset,
        }
        benchmark_from_args(**benchmark_args)
    else:
        benchmark_from_file(input_file=Path(args.input_file))
