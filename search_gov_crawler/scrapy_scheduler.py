import json
import logging
import os
import subprocess
from pathlib import Path

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from pythonjsonlogger.json import JsonFormatter

from search_gov_crawler.search_gov_spiders.extensions.json_logging import LOG_FMT
from search_gov_crawler.search_gov_spiders.utility_files.init_schedule import SpiderSchedule

logging.basicConfig(level=logging.INFO)
log = logging.getLogger()
log.handlers[0].setFormatter(JsonFormatter(fmt=LOG_FMT))

CRAWL_SITES_FILE = Path(__file__).parent / "search_gov_spiders" / "utility_files" / "crawl-sites.json"


def run_scrapy_crawl(spider: str, allow_query_string: bool, allowed_domains: str, start_urls: str) -> None:
    """Runs `scrapy crawl` command as a subprocess given the allowed arguments"""

    scrapy_env = os.environ.copy()
    scrapy_env["PYTHONPATH"] = str(Path(__file__).parent.parent)

    subprocess.run(
        f"scrapy crawl {spider} -a allow_query_string={allow_query_string} -a allowed_domains={allowed_domains} -a start_urls={start_urls}",
        check=True,
        cwd=Path(__file__).parent,
        env=scrapy_env,
        executable="/bin/bash",
        shell=True,
    )
    msg = (
        "Successfully completed scrapy crawl with args "
        "spider=%s, allow_query_string=%s, allowed_domains=%s, start_urls=%s"
    )
    log.info(msg, spider, allow_query_string, allowed_domains, start_urls)


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
                    crawl_site["allow_query_string"],
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


if __name__ == "__main__":
    start_scrapy_scheduler(input_file=CRAWL_SITES_FILE)
