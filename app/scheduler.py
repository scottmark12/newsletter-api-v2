from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
import logging
from .config import TIMEZONE
from . import crawler, scoring, publish
from .db import init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("scheduler")

def job_ingest():
    log.info("Running ingest...")
    res = crawler.run()
    log.info(f"Ingest result: {res}")

def job_score():
    log.info("Running score...")
    res = scoring.run(limit=100)
    log.info(f"Score result: {res}")

def job_publish():
    log.info("Running publish dryrun (daily)…")
    html = publish.dryrun()
    log.info(f"Publish dryrun length: {len(html)} chars")

if __name__ == "__main__":
    init_db()
    tz = timezone(TIMEZONE)
    sched = BlockingScheduler(timezone=tz)

    # crawl every hour
    sched.add_job(job_ingest, IntervalTrigger(hours=1, timezone=tz), id="ingest")
    # score every 3 hours
    sched.add_job(job_score, IntervalTrigger(hours=3, timezone=tz), id="score")
    # “publish” (dryrun) daily at 07:00 local time
    sched.add_job(job_publish, CronTrigger(hour=7, minute=0, timezone=tz), id="publish_dryrun")

    log.info("Scheduler started")
    sched.start()
