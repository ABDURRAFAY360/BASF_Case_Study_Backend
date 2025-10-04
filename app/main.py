from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router
from pathlib import Path
import json

from app.db.base import Base
from app.db.session import engine, AsyncSessionLocal
from app.repositories.user_repo import UserRepository
from app.repositories.book_repo import BookRepository
from app.core.security import hash_password
from app.core.logging import setup_logger
from app.services.book_service import BookService

logger = setup_logger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/",
    redoc_url=None,
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Startup tasks ----------
async def init_db() -> None:
    """Create database schema."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_users() -> None:
    """Seed users from JSON file if available."""
    seed_path = Path(settings.USERS_SEED_FILE).resolve()
    if not seed_path.exists():
        logger.info("No user seed file found, skipping user seeding.")
        return

    try:
        rows = json.loads(seed_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in user seed file: {e}")
        return

    if not rows:
        logger.info("User seed file is empty, skipping.")
        return

    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)
        to_insert = [
            {"username": row["username"], "password": hash_password(row["password"])}
            for row in rows
        ]
        inserted = await repo.bulk_upsert(to_insert)
        logger.info("Seeded %s users.", inserted)


async def seed_books() -> None:
    #Seed books from JSON file.
    # async with AsyncSessionLocal() as session:
    #     repo = BookRepository(session)
    #     if await repo.seed_books():
    #         logger.info("Books seeded successfully.")
    #     else:
    #         logger.info("No book seed file found, skipping book seeding.")
    # Seed books from JSON file.
    async with AsyncSessionLocal() as session:
        book_service = BookService(session)
        if await book_service.seed_from_google(query="python development", limit=15):
            logger.info("Books seeded successfully.")
        else:
            logger.info("No books found, skipping book seeding.")


@app.on_event("startup")
async def on_startup() -> None:
    """Initialize database and seed data."""
    await init_db()
    await seed_users()
    await seed_books()


# ---------- Routers ----------
app.include_router(api_router, prefix=settings.API_V1_STR)
