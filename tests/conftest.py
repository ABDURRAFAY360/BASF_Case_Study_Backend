import os
import asyncio
import pytest
import pytest_asyncio
from sqlalchemy import text

# 1) force SQLite-in-memory for tests BEFORE importing app modules
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from app.db import session as db_session  # import module (not names)
from app.db.base import Base


# single event loop for the whole session
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# 2) switch engine to sqlite memory and create schema once, on a dedicated conn
@pytest_asyncio.fixture(scope="session", autouse=True)
async def use_sqlite_memory():
    db_session.override_database(os.environ["DATABASE_URL"])
    async with db_session.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # no teardown needed for in-memory


# 3) clean tables before each test on a dedicated connection
@pytest_asyncio.fixture(autouse=True)
async def clean_db():
    async with db_session.engine.begin() as conn:
        # order because of FK reviews->books
        await conn.execute(text("DELETE FROM reviews;"))
        await conn.execute(text("DELETE FROM books;"))
        await conn.execute(text("DELETE FROM users;"))
    yield


# 4) provide a fresh AsyncSession per test
@pytest_asyncio.fixture
async def db():
    async with db_session.AsyncSessionLocal() as s:
        yield s
