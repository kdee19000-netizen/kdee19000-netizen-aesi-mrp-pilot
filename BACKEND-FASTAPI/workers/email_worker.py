"""
Email Worker (Celery task)

Dispatches email notifications asynchronously.
"""

import logging
import os

logger = logging.getLogger(__name__)

try:
    from celery import Celery  # type: ignore

    celery_app = Celery("aesi_mrp", broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"))

    @celery_app.task(name="workers.email_worker.send_email_task")
    def send_email_task(to: str, subject: str, body: str):
        """Celery task to send an email via SendGrid."""
        import asyncio

        from services.notification_service import NotificationService

        asyncio.run(NotificationService.send_email(to, subject, body))

except ImportError:
    logger.warning("Celery not available – email tasks will run synchronously")
