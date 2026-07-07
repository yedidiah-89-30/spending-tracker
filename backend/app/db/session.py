from typing import Generator

from sqlalchemy.orm import Session

from app.db.base import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding one Session per request, always closed
    afterwards regardless of success/failure."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
