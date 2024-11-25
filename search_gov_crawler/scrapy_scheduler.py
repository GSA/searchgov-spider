import argparse
import json
import logging
import subprocess
import time
import os
from datetime import datetime, UTC, timedelta
from pathlib import Path

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from pythonjsonlogger.json import JsonFormatter

from search_gov_crawler.search_gov_spiders.extensions.json_logging import LOG_FMT
from search_gov_crawler.search_gov_spiders.utility_files.init_schedule import SpiderSchedule

logging.basicConfig(level=logging.INFO)
log = logging.getLogger()
log.handlers[0].setFormatter(JsonFormatter(fmt=LOG_FMT))

BENCHMARK_RUN = bool(os.environ.get("BENCHMARK_RUN", "False").lower() == "true")
CRAWL_SITES_FILE = Path(__file__).parent / "search_gov_spiders" / "utility_files" / "crawl-sites.json"


def run_scrapy_crawl(spider: str, allowed_domains: str, start_urls: str) -> None:
    """Runs `scrapy crawl` command as a subprocess given the allowed arguments"""

    scrapy_env = os.environ.copy()
    scrapy_env["PYTHONPATH"] = str(Path(__file__).parent.parent)

    subprocess.run(
        f"scrapy crawl {spider} -a allowed_domains={allowed_domains} -a start_urls={start_urls}",
        check=True,
        cwd=Path(__file__).parent,
        env=scrapy_env,
        executable="/bin/bash",
        shell=True,
    )
    log.info(
        "Successfully completed scrapy crawl with args spider=%s, allowed_domains=%s, start_urls=%s",
        spider,
        allowed_domains,
        start_urls,
    )


def transform_crawl_sites(crawl_sites: list[dict]) -> list[dict]:
    """Transform crawl sites records into a format that can be used to"""

    transformed_crawl_sites = []
    schedule = SpiderSchedule()

    for crawl_site in crawl_sites:
        job_name = str(crawl_site["name"])
        schedule_slot = schedule.get_next_slot()
        transformed_crawl_sites.append(
            {
                "func": run_scrapy_crawl,
                "id": job_name.lower().replace(" ", "-").replace("---", "-"),
                "name": job_name,
                "trigger": CronTrigger(
                    year="*",
                    month="*",
                    day="*",
                    week="*",
                    day_of_week=schedule_slot.day,
                    hour=schedule_slot.hour,
                    minute=schedule_slot.minute,
                    second=0,
                    timezone="UTC",
                    jitter=0,
                ),
                "args": [
                    "domain_spider" if not crawl_site["handle_javascript"] else "domain_spider_js",
                    crawl_site["allowed_domains"],
                    crawl_site["starting_urls"],
                ],
            }
        )

    return transformed_crawl_sites


def start_scrapy_scheduler(input_file: Path) -> None:
    """Initializes schedule from input file, schedules jobs and runs scheduler"""

    # Load and transform crawl sites
    crawl_sites = json.loads(input_file.read_text(encoding="UTF-8"))
    apscheduler_jobs = transform_crawl_sites(crawl_sites)

    # Initalize scheduler
    max_workers = min(32, (os.cpu_count() or 1) + 4)  # default from concurrent.futures

    scheduler = BlockingScheduler(
        jobstores={"memory": MemoryJobStore()},
        executors={"default": ThreadPoolExecutor(max_workers)},
        job_defaults={"coalesce": False, "max_instances": 1},
        timezone="UTC",
    )

    # Schedule Jobs
    for apscheduler_job in apscheduler_jobs:
        scheduler.add_job(**apscheduler_job, jobstore="memory")

    # Run Scheduler
    scheduler.start()


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
        "func": run_scrapy_crawl,
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
    if not BENCHMARK_RUN:
        start_scrapy_scheduler(input_file=CRAWL_SITES_FILE)
    else:
        parser = argparse.ArgumentParser(description="Run a scrapy schedule or benchmark based on input.")
        parser.add_argument("--allowed_domains", type=str, help="domains allowed to crawl", required=True)
        parser.add_argument("--starting_urls", type=str, help="url used to start crawl", required=True)
        parser.add_argument("--handle_js", action=argparse.BooleanOptionalAction, help="Flag to enable javascript")
        parser.add_argument("--runtime_offset", type=int, default=5, help="Number of seconds to offset job start")
        args = parser.parse_args()

        log.info("***RUNNING BENCHMARK TEST***")
        benchmark_args = {
            "allowed_domains": args.allowed_domains,
            "starting_urls": args.starting_urls,
            "handle_javascript": args.handle_js,
            "runtime_offset_seconds": args.runtime_offset,
        }
        benchmark_scrapy(**benchmark_args)
