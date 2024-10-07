import json
import sqlite3
import os
import subprocess
from collections import namedtuple

from datetime import datetime, timedelta, UTC
from pathlib import Path
from typing import Optional

SpiderScheduleSlot = namedtuple("SpiderScheduleSlot", ["day", "hour", "minute"])


class SpiderSchedule:
    """
    Scheduler that will output a single round of day, hour, week time slots.  If more
    slots are needed the class must be modified.
    """

    start_datetime: datetime
    end_datetime: datetime
    last_slot_filled: Optional[datetime] | None
    slot_offset: timedelta

    def __init__(self):
        self.start_datetime = datetime(2024, 12, 2, 3, 30, 0, tzinfo=UTC)
        self.end_datetime = datetime(2024, 12, 6, 21, 30, 0, tzinfo=UTC)
        self.last_slot_filled = None
        self.slot_offset = timedelta(hours=2)

    def get_next_slot(self) -> SpiderScheduleSlot:
        """Return next available slot as a tuple of day, hour, minute"""

        if not self.last_slot_filled:  # first slot
            self.last_slot_filled = self.start_datetime
        else:
            self.last_slot_filled = self.last_slot_filled + self.slot_offset

            if self.last_slot_filled > self.end_datetime:
                raise NotImplementedError(
                    f"This class does not support assignment beyond {self.end_datetime.strftime("%a %H:%M")}"
                )

            while not self._is_valid_slot(self.last_slot_filled):
                self.last_slot_filled = self.last_slot_filled + self.slot_offset

        return SpiderScheduleSlot(
            self.last_slot_filled.strftime("%a").lower(),
            self.last_slot_filled.strftime("%H"),
            self.last_slot_filled.strftime("%M"),
        )

    def _is_valid_slot(self, potential_slot: datetime) -> bool:
        """Determine if potential slot is valid based on start and end dates and maintenance window"""

        # do not schedule before 0300 or after 2300
        slot_hour = potential_slot.hour
        if slot_hour < self.start_datetime.hour or slot_hour > self.end_datetime.hour:
            return False

        # do not schedule during maintenance winddow
        if potential_slot.weekday() == 2 and potential_slot.hour > 14 and potential_slot.hour < 21:
            return False

        return True


def truncate_table(conn: sqlite3.Connection, table_name: str):
    """Delete all data in a given table"""
    delete_stmt = f"DELETE FROM {table_name}"
    conn.execute(delete_stmt)
    conn.commit()


def get_data_dir() -> Path:
    """
    Helps find database files in local venv.  Does not cover all cases.  The DATA_PATH environment
    variable is used by scrapydweb to place the database files (along with other files).  Set DATA_PATH
    if encountering issues.
    """
    data_dir = os.getenv("DATA_PATH")

    if not data_dir:
        which_proc = subprocess.run(["which", "scrapydweb"], stdout=subprocess.PIPE, check=True)
        venv_python = Path(which_proc.stdout.decode("UTF-8").rstrip())
        lib = venv_python.parent.parent / "lib"
        venv_version = [child for child in lib.iterdir()][0]
        return venv_version / "site-packages/scrapydweb/data"

    return Path(data_dir)


def init_schedule():
    """
    Initalize a schedule in scrapydweb using the info in the crawl sites json file.  Ideally
    this should be used for development or for standing up a new environment.  Attention should
    be paid to the location of the scrapydweb databases in the environment in which this is run.
    """

    # read crawl sites from file and transform into scrapydweb tasks format.
    crawl_sites_file = Path(__file__).parent / "crawl-sites.json"
    crawl_sites = json.loads(crawl_sites_file.read_text(encoding="UTF-8"))

    scrapydweb_tasks = []
    current_timestamp = datetime.now(tz=UTC).strftime("%Y-%m-%d %H:%M:%S%:z")
    schedule = SpiderSchedule()
    for idx, crawl_site in enumerate(crawl_sites):
        job_name = str(crawl_site["name"])
        schedule_slot = schedule.get_next_slot()
        scrapydweb_tasks.append(
            {
                "id": idx + 1,
                "name": job_name,
                "triger": "cron",
                "create_time": current_timestamp,
                "update_time": current_timestamp,
                "project": "search_gov_spiders",
                "version": "default: the latest version",
                "spider": "domain_spider" if not crawl_site["handle_javascript"] else "domain_spider_js",
                "jobid": job_name.lower().replace(" ", "-").replace("---", "-"),
                "settings_arguments": str(
                    {
                        "allowed_domains": crawl_site["allowed_domains"],
                        "setting": [],
                        "start_urls": crawl_site["starting_urls"],
                    }
                ),
                "selected_nodes": "[1]",
                "year": "*",
                "month": "*",
                "day": "*",
                "week": "*",
                "day_of_week": schedule_slot.day,
                "hour": schedule_slot.hour,
                "minute": schedule_slot.minute,
                "second": "0",
                "start_date": None,
                "end_date": None,
                "timezone": "UTC",
                "jitter": 0,
                "misfire_grace_time": 600,
                "coalesce": "True",
                "max_instances": 1,
            }
        )

    # Locate scrapydweb database files and init
    data_dir = get_data_dir()
    ap_scheduler_db = data_dir / "database/apscheduler.db"
    timer_tasks_db = data_dir / "database/timer_tasks.db"

    with sqlite3.connect(ap_scheduler_db) as ap_scheduler_conn:
        truncate_table(ap_scheduler_conn, "apscheduler_jobs")

    with sqlite3.connect(timer_tasks_db) as timer_tasks_conn:
        truncate_table(timer_tasks_conn, "task")
        truncate_table(timer_tasks_conn, "task_job_result")
        truncate_table(timer_tasks_conn, "task_result")

        timer_tasks_conn.executemany(
            """
            INSERT INTO task VALUES(:id, :name, :triger, :create_time, :update_time, :project,
                                    :version, :spider, :jobid, :settings_arguments, :selected_nodes,
                                    :year, :month, :day, :week, :day_of_week, :hour, :minute, :second,
                                    :start_date, :end_date, :timezone, :jitter, :misfire_grace_time,
                                    :coalesce, :max_instances)""",
            scrapydweb_tasks,
        )


if __name__ == "__main__":
    init_schedule()
