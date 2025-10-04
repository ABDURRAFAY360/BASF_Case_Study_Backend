# tests/conftest.py
import asyncio
import pytest
import pytest_asyncio
from sqlalchemy import text

from app.db.base import Base
from app.db.session import engine, AsyncSessionLocal


# -------- ensure pytest-asyncio event loop exists for async tests --------
@pytest.fixture(scope="session")
def event_loop():
    """Create a fresh event loop for the whole test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# -------- create ALL tables once, drop at end of session --------
@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_schema_once():
    # make sure we create the schema on the SAME engine used in tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # yield control to the test session
    yield
    # optional: drop all at end (useful when not in-memory)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# -------- function-scoped DB cleanup so every test starts fresh --------
@pytest_asyncio.fixture
async def clean_db():
    """Truncate tables between tests. Order matters due to FKs."""
    async with AsyncSessionLocal() as s:
        # disable FK checks temporarily for SQLite
        await s.execute(text("PRAGMA foreign_keys = OFF;"))
        # delete in child->parent order if you have FKs:
        # reviews -> books -> users (adjust to your actual tables)
        try:
            await s.execute(text("DELETE FROM reviews;"))
        except Exception:
            pass
        try:
            await s.execute(text("DELETE FROM books;"))
        except Exception:
            pass
        try:
            await s.execute(text("DELETE FROM users;"))
        except Exception:
            pass
        await s.execute(text("PRAGMA foreign_keys = ON;"))
        await s.commit()
    yield  # test runs
