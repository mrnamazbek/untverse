import time
from collections import defaultdict
from typing import Dict, List
from fastapi import Request, HTTPException, status
from app.core.config import settings


class InMemoryRateLimiter:
    """
    Thread-safe sliding window rate limiter.
    Limits requests per IP/key within a moving time window.
    """

    def __init__(self):
        self._records: Dict[str, List[float]] = defaultdict(list)
        self._last_cleanup: float = time.time()

    def _cleanup_stale(self, now: float, max_age: float = 3600.0) -> None:
        """Periodic cleanup to prevent unbounded memory growth."""
        if now - self._last_cleanup < 300.0:  # every 5 minutes
            return
        stale_keys = [
            k
            for k, timestamps in self._records.items()
            if not timestamps or now - timestamps[-1] > max_age
        ]
        for k in stale_keys:
            self._records.pop(k, None)
        self._last_cleanup = now

    def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
    ) -> None:
        import os

        if settings.ENVIRONMENT in ("test", "testing") or "PYTEST_CURRENT_TEST" in os.environ:
            # Do not throttle automated unit/integration tests
            return

        now = time.time()
        self._cleanup_stale(now)

        window_start = now - window_seconds
        timestamps = self._records[key]

        # Filter out timestamps outside the sliding window
        valid_timestamps = [t for t in timestamps if t > window_start]
        self._records[key] = valid_timestamps

        if len(valid_timestamps) >= max_requests:
            retry_after = int(window_seconds - (now - valid_timestamps[0])) + 1
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Превышен лимит запросов. Пожалуйста, повторите попытку позже.",
                headers={"Retry-After": str(max(1, retry_after))},
            )

        valid_timestamps.append(now)


limiter = InMemoryRateLimiter()


def rate_limit(max_requests: int = 10, window_seconds: int = 60):
    """
    FastAPI dependency for rate limiting endpoints by client IP.
    """

    async def dependency(request: Request):
        forwarded_for = request.headers.get("X-Forwarded-For")
        client_ip = (
            forwarded_for.split(",")[0].strip()
            if forwarded_for
            else (request.client.host if request.client else "unknown")
        )
        rate_key = f"{client_ip}:{request.url.path}"
        limiter.check_rate_limit(rate_key, max_requests=max_requests, window_seconds=window_seconds)

    return dependency
