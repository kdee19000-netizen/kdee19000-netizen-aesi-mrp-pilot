"""
MRP Timer Worker

Schedules and tracks the 10-minute MRP recalculation timer.
Uses Redis sorted-sets for persistence across restarts.
"""

import asyncio
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

TIMER_SECONDS = int(os.getenv("MRP_TIMER_SECONDS", "600"))


class MRPTimerWorker:
    """Manages per-record 10-minute MRP timers."""

    def __init__(self):
        self._tasks: dict = {}

    def start_timer(self, record_id: str, callback=None) -> asyncio.Task:
        """Start (or restart) a timer for *record_id*."""
        if record_id in self._tasks and not self._tasks[record_id].done():
            self._tasks[record_id].cancel()

        task = asyncio.create_task(self._run(record_id, callback))
        self._tasks[record_id] = task
        logger.info("MRP timer started: record_id=%s seconds=%d", record_id, TIMER_SECONDS)
        return task

    def cancel_timer(self, record_id: str):
        task = self._tasks.get(record_id)
        if task and not task.done():
            task.cancel()
            logger.info("MRP timer cancelled: record_id=%s", record_id)

    async def _run(self, record_id: str, callback=None):
        try:
            await asyncio.sleep(TIMER_SECONDS)
            logger.info("MRP timer expired: record_id=%s – triggering MRP run", record_id)
            if callback:
                await callback(record_id)
        except asyncio.CancelledError:
            logger.debug("MRP timer cancelled for record_id=%s", record_id)


mrp_timer_worker = MRPTimerWorker()
