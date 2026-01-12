"""Pytest configuration and fixtures for testing."""

import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    """Set environment variables for tests before any imports."""
    os.environ["DATABASE_URL"] = "sqlite:///./test_app.db"
    os.environ["API_KEY_ENABLED"] = "true"
    os.environ["API_KEY"] = "TEST_KEY"
    os.environ["LOG_LEVEL"] = "WARNING"
    yield
    # Cleanup test database after all tests
    import pathlib

    db_path = pathlib.Path("test_app.db")
    if db_path.exists():
        db_path.unlink()


@pytest.fixture()
def client():
    """Create a test client with a fresh database for each test."""
    from app.db.base import Base
    from app.db.session import get_engine
    from app.main import create_app

    # Clear and recreate the database schema
    engine = get_engine()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    app = create_app()
    with TestClient(app) as test_client:
        yield test_client

    # Close any remaining connections
    engine.dispose()


@pytest.fixture()
def headers():
    """Return headers with API key for authenticated requests."""
    return {"X-API-Key": "TEST_KEY"}
