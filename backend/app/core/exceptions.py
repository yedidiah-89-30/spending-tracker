"""Domain-level exceptions.

Repositories and services raise these instead of HTTPException directly,
keeping them free of any HTTP/framework concerns and independently
testable. `register_exception_handlers` (called once from main.py) maps
each of these to the right HTTP response with one consistent JSON shape:
{"error_code": "...", "detail": "..."}.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger("app")


class AppError(Exception):
    """Base class for all handled application errors."""

    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "app_error"

    def __init__(self, detail: str = "An application error occurred."):
        self.detail = detail
        super().__init__(detail)


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "not_found"

    def __init__(self, detail: str = "Resource not found."):
        super().__init__(detail)


class ConflictError(AppError):
    status_code = status.HTTP_409_CONFLICT
    error_code = "conflict"

    def __init__(self, detail: str = "Resource already exists."):
        super().__init__(detail)


class ValidationAppError(AppError):
    status_code = 422
    error_code = "validation_error"

    def __init__(self, detail: str = "Invalid input."):
        super().__init__(detail)


class UnauthorizedError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "unauthorized"

    def __init__(self, detail: str = "Authentication required or invalid credentials."):
        super().__init__(detail)


class ForbiddenError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "forbidden"

    def __init__(self, detail: str = "You don't have access to this resource."):
        super().__init__(detail)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        # Never log request bodies here (would risk leaking passwords/tokens) -
        # only the error code, message, and route.
        logger.warning("%s: %s (%s %s)", exc.error_code, exc.detail, request.method, request.url.path)
        return JSONResponse(
            status_code=exc.status_code,
            content={"error_code": exc.error_code, "detail": exc.detail},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error_code": "internal_error", "detail": "An unexpected error occurred."},
        )
