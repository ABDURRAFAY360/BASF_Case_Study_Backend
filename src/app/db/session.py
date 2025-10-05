from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool
from app.core.config import settings

_engine = None
_SessionLocal = None

def _make_engine(url: str):
    if url.startswith("sqlite+aiosqlite"):
        # single in-memory DB shared across sessions
        return create_async_engine(
            url,
            echo=False,
            future=True,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    # default (Postgres etc.)
    return create_async_engine(url, echo=False, future=True, pool_pre_ping=True)

def _ensure():
    global _engine, _SessionLocal
    if _engine is None or _SessionLocal is None:
        _engine = _make_engine(settings.DATABASE_URL)
        _SessionLocal = async_sessionmaker(_engine, expire_on_commit=False, class_=AsyncSession)

def get_engine():
    _ensure()
    return _engine

def get_sessionmaker():
    _ensure()
    return _SessionLocal

# public names used everywhere else
engine = get_engine()
AsyncSessionLocal = get_sessionmaker()

def override_database(url: str):
    """Tests call this to force a different database URL (e.g. in-memory SQLite)."""
    global _engine, _SessionLocal, engine, AsyncSessionLocal
    _engine = _make_engine(url)
    _SessionLocal = async_sessionmaker(_engine, expire_on_commit=False, class_=AsyncSession)
    engine = _engine
    AsyncSessionLocal = _SessionLocal

async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session