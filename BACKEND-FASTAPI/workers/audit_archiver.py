"""
Audit Archiver Worker (Celery task)

Periodically archives old audit logs to cold storage (S3 / Azure Blob).
"""

import logging
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

ARCHIVE_AFTER_DAYS = int(os.getenv("AUDIT_ARCHIVE_AFTER_DAYS", "90"))

try:
    from celery import Celery  # type: ignore
    from celery.schedules import crontab  # type: ignore

    celery_app = Celery("aesi_mrp", broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"))

    celery_app.conf.beat_schedule = {
        "archive-audit-logs-daily": {
            "task": "workers.audit_archiver.archive_old_logs",
            "schedule": crontab(hour=2, minute=0),  # 02:00 every day
        }
    }

    @celery_app.task(name="workers.audit_archiver.archive_old_logs")
    def archive_old_logs():
        """Move audit log entries older than ARCHIVE_AFTER_DAYS to cold storage."""
        cutoff = datetime.utcnow() - timedelta(days=ARCHIVE_AFTER_DAYS)
        logger.info("Archiving audit logs older than %s", cutoff.isoformat())
        # TODO: implement S3/Azure Blob export and mark rows as archived

except ImportError:
    logger.warning("Celery not available – audit archiver will not run")
