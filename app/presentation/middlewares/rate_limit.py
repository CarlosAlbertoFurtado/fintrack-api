"""
Simple in-memory rate limiter using sliding window.
In production you'd want to use Redis for this, but for a single-instance
API this works fine. Keeps track of request counts per IP.
"""

import time
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.rpm = requests_per_minute
        self.window = 60  # seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # skip health check
        if request.url.path == "/health":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # clean old entries outside the window
        self._hits[client_ip] = [
            t for t in self._hits[client_ip]
            if now - t < self.window
        ]

        if len(self._hits[client_ip]) >= self.rpm:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Max {self.rpm} requests per minute."
            )

        self._hits[client_ip].append(now)

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.rpm)
        response.headers["X-RateLimit-Remaining"] = str(
            self.rpm - len(self._hits[client_ip])
        )
        return response
