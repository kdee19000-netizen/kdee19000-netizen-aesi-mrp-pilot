"""
Rate Limit Middleware

Simple in-memory sliding-window rate limiter.
In production use Redis-backed rate limiting (e.g. slowapi).
"""

import logging
import os
import time
from collections import defaultdict, deque
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)

MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX", "100"))
WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW", "60"))


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding-window rate limiter keyed by client IP address."""

    def __init__(self, app, max_requests: int = MAX_REQUESTS, window: int = WINDOW_SECONDS):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self._buckets: dict = defaultdict(deque)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        bucket = self._buckets[client_ip]

        # Evict old entries outside the window
        while bucket and bucket[0] <= now - self.window:
            bucket.popleft()

        if len(bucket) >= self.max_requests:
            logger.warning("Rate limit exceeded for %s", client_ip)
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please retry later."},
            )

        bucket.append(now)
        return await call_next(request)
