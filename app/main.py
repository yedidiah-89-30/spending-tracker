import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config.settings import get_settings
from app.core.exceptions import register_exception_handlers
from app.middleware.logging_middleware import register_logging_middleware
from app.middleware.security_headers import register_security_headers

settings = get_settings()


def configure_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        stream=sys.stdout,
    )
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title=settings.APP_NAME,
        description="Backend API for the Spending Tracker application.",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_security_headers(app)
    register_logging_middleware(app)
    register_exception_handlers(app)

    app.include_router(api_router)

    @app.get("/health", tags=["Health"], summary="Liveness/readiness check")
    def health_check() -> dict:
        return {"status": "ok", "environment": settings.ENVIRONMENT}

    return app


app = create_app()
