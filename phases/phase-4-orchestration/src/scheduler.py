from __future__ import annotations

"""
High-level scheduling architecture for the Groww Mutual Fund FAQ Assistant.

Responsibilities:
- Define an APScheduler-based background scheduler that:
  - Runs the scraper (`fetch_daily`) and ingestor (`ingest_daily`) once every 24 hours.
  - Supports an on-demand “run now” pipeline trigger.
- Provide a singleton-style API so Streamlit (`app.py`) can safely start the scheduler
  exactly once during app initialization.
"""

import logging
import sys
from datetime import datetime, date
from pathlib import Path
from typing import Any, Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from zoneinfo import ZoneInfo

# Add phase directories to Python path for imports
_current_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_current_dir / "phase-1-collection"))
sys.path.insert(0, str(_current_dir / "phase-2-processing"))
sys.path.insert(0, str(_current_dir / "phase-3-retrieval"))

from src.scraper import fetch_daily
from src.ingest import ingest_daily

logger = logging.getLogger(__name__)

SCHEDULER_JOB_ID = "daily_scrape_and_ingest"

# Module-level singleton for the scheduler
_scheduler: Optional[BackgroundScheduler] = None


def get_scheduler() -> BackgroundScheduler:
    """
    Return (or lazily create) a global APScheduler instance.

    Intended usage:
    - Streamlit `app.py` will call this and then `start_scheduler_once()`.
    """
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler()
    return _scheduler


def schedule_daily_job(scheduler: BackgroundScheduler) -> None:
    """
    Register a job that triggers the scrape + ingest pipeline every day at 10 AM IST.
    """
    ist = ZoneInfo("Asia/Kolkata")
    
    # Remove existing job if any
    try:
        scheduler.remove_job(SCHEDULER_JOB_ID)
    except:
        pass
    
    scheduler.add_job(
        run_pipeline_once,
        trigger=CronTrigger(hour=10, minute=0, timezone=ist),
        id=SCHEDULER_JOB_ID,
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=3600
    )
    logger.info(f"Scheduled daily job at 10:00 AM IST (Job ID: {SCHEDULER_JOB_ID})")


def run_pipeline_once(run_time: Optional[datetime] = None) -> None:
    """
    Manually execute one end-to-end pipeline run:
    - Call `scraper.fetch_daily(...)`.
    - Then call `ingest.ingest_daily(...)`.

    This function is intended to be used:
    - By the scheduled job.
    - Optionally from the Streamlit UI for manual re-runs.
    """
    try:
        run_date = run_time.date() if run_time else date.today()
        logger.info(f"Starting pipeline run for {run_date}")
        
        # Step 1: Scrape
        scrape_summary = fetch_daily(run_date=run_date)
        logger.info(f"Scrape completed: {scrape_summary}")
        
        # Step 2: Ingest
        ingest_summary = ingest_daily(run_date=run_date)
        logger.info(f"Ingest completed: {ingest_summary}")
        
    except Exception as e:
        logger.error(f"Pipeline run failed: {e}")


def start_scheduler_once() -> BackgroundScheduler:
    """
    Start the APScheduler instance if it has not been started yet.
    """
    scheduler = get_scheduler()
    
    if not scheduler.running:
        schedule_daily_job(scheduler)
        scheduler.start()
        logger.info("Background scheduler started.")
        
        # Log next run time
        job = scheduler.get_job(SCHEDULER_JOB_ID)
        if job and job.next_run_time:
            logger.info(f"Next scheduled run: {job.next_run_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    else:
        logger.info("Scheduler already running.")
    
    return scheduler


if __name__ == "__main__":
    # Optional manual entry-point for local testing of the scheduler.
    logging.basicConfig(level=logging.INFO)
    start_scheduler_once()

