import logging
import time
import uuid

from fastapi import FastAPI, Request

logger = logging.getLogger("app.requests")


def register_logging_middleware(app: FastAPI) -> None:
    """Logs method/path/status/duration for every request and stamps an
    X-Request-ID header so a request can be traced through logs. Bodies are
    never logged - auth payloads contain passwords/tokens."""

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "[%s] %s %s -> %s (%.1fms)",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response
