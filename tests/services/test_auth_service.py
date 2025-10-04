import pytest
from jose import jwt

from app.core.config import settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import engine, AsyncSessionLocal
from app.models.user import User
from app.services.auth_service import AuthUseCases
from fastapi import HTTPException


# --- session-scoped DB setup once per test session ---
@pytest.fixture(scope="session", autouse=True)
async def create_schema():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# --- per-test clean DB & seed helper ---
async def _truncate_all():
    # For SQLite, easiest is to drop & recreate; but that's heavy.
    # Instead, just delete users table rows for this test suite.
    async with AsyncSessionLocal() as s:
        await s.execute(User.__table__.delete())
        await s.commit()


@pytest.mark.asyncio
async def test_login_success_returns_valid_jwt():
    await _truncate_all()

    # seed a user directly in the DB (store HASH in 'password' column)
    async with AsyncSessionLocal() as s:
        u = User(username="abdur", password=hash_password("password123"))
        s.add(u)
        await s.commit()

    # call service
    async with AsyncSessionLocal() as s:
        token = await AuthUseCases(s).login("abdur", "password123")

    # verify JWT decodes and 'sub' matches username
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded.get("sub") == "abdur"


@pytest.mark.asyncio
async def test_login_wrong_password_raises_401():
    await _truncate_all()

    async with AsyncSessionLocal() as s:
        s.add(User(username="rafay", password=hash_password("testpass")))
        await s.commit()

    async with AsyncSessionLocal() as s:
        with pytest.raises(Exception) as excinfo:
            await AuthUseCases(s).login("rafay", "testfail")
        # FastAPI raises HTTPException in service (status_code=401)
        # we just check it's an HTTPException and code is 401

        assert isinstance(excinfo.value, HTTPException)
        assert getattr(excinfo.value, "status_code", None) == 401
