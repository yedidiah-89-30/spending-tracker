from fastapi import FastAPI, Request


def register_security_headers(app: FastAPI) -> None:
    """Adds a baseline set of security headers to every response.
    Cheap, framework-level hardening that has nothing to do with business
    logic, so it lives in middleware rather than in individual routes."""

    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response
