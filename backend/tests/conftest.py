"""Test configuration.

Uses an in-memory SQLite database instead of Postgres for speed and zero
infra requirements when running `pytest` locally. This is safe for Sprint 1
because User/RefreshToken use only portable column types (no Postgres-only
types like JSONB/UUID); if a later sprint introduces Postgres-specific
types, those tests should instead run against a real Postgres (e.g. the one
in docker-compose.yml) via a DATABASE_URL override.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture()
def db_session():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """The rate limiter keeps counters in a module-level dict so it survives
    across requests within a real process - but that means it also
    (undesirably) survives across tests unless we clear it here."""
    from app.utils.rate_limit import _hits

    _hits.clear()
    yield
    _hits.clear()


@pytest.fixture()
def client(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
