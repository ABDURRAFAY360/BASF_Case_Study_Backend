from __future__ import annotations

from pathlib import Path
import json
from typing import Any, Dict, Iterable, List

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router

from app.db.base import Base
from app.db.session import engine, AsyncSessionLocal

from app.repositories.user_repo import UserRepository
from app.core.security import hash_password
from app.core.logging import setup_logger
from app.services.book_service import BookService


# --- Logging -----------------------------------------------------------------
logger = setup_logger(__name__)


# --- App creation & configuration -------------------------------------------
def _create_fastapi_app() -> FastAPI:
    """
    Create the FastAPI app instance with the same public surface and behavior.
    """
    return FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        docs_url="/",
        redoc_url=None,
        openapi_url="/openapi.json",
    )


def _configure_cors(app: FastAPI) -> None:
    """
    Configure permissive CORS (unchanged from original).
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def _register_routes(app: FastAPI) -> None:
    """
    Keep API v1 mounted under configured prefix.
    """
    app.include_router(api_router, prefix=settings.API_V1_STR)


# Instantiate and configure app (same timing and effect as before).
app = _create_fastapi_app()
_configure_cors(app)
_register_routes(app)


# --- Utility helpers ---------------------------------------------------------
def _read_json_array(path: Path) -> List[Dict[str, Any]]:
    """
    Read a JSON file expected to contain an array of objects.
    Returns [] on missing file or invalid JSON/shape.
    """
    if not path.exists():
        logger.info("Seed file %s does not exist. Skipping.", path)
        return []

    try:
        content = path.read_text(encoding="utf-8")
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse JSON from %s: %s", path, exc)
        return []

    if not isinstance(data, list):
        logger.error("Seed file %s must contain a JSON array. Skipping.", path)
        return []

    return data


# --- DB schema init ----------------------------------------------------------
async def init_db() -> None:
    """Create database schema (idempotent)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# --- User seeding (split into focused steps) ---------------------------------
def _users_seed_path() -> Path:
    """
    Resolve the user seed file path from settings (kept identical).
    """
    return Path(settings.USERS_SEED_FILE).resolve()


def _load_raw_user_rows(path: Path) -> List[Dict[str, Any]]:
    """
    Load raw user rows from seed JSON, with logging consistent to original intent.
    """
    logger.info("Attempting to seed users from %s", path)
    rows = _read_json_array(path)
    if not rows:
        logger.info("No users to seed. Skipping.")
    return rows


def _validate_user_row(row: Dict[str, Any]) -> bool:
    """
    Ensure required fields exist; keeps logic permissive (no extra validation).
    """
    return "username" in row and "password" in row


def _hash_user_rows(rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Prepare rows for upsert: hash passwords and keep keys unchanged otherwise.
    """
    prepared = [
        {
            "username": row["username"],
            "password": hash_password(row["password"]),
        }
        for row in rows
        if _validate_user_row(row)
    ]
    if not prepared:
        logger.info("No valid user rows found in seed file. Skipping.")
    return prepared


async def _upsert_users(rows: List[Dict[str, Any]]) -> None:
    """
    Upsert users through repository and log count (same behavior).
    """
    if not rows:
        return

    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)
        inserted = await repo.bulk_upsert(rows)
        logger.info("Seeded %s users.", inserted)


async def seed_users() -> None:
    """
    Orchestrate user seeding using small helpers (logic unchanged).
    """
    seed_path = _users_seed_path()
    raw_rows = _load_raw_user_rows(seed_path)
    prepared_rows = _hash_user_rows(raw_rows)
    await _upsert_users(prepared_rows)


# --- Book seeding (split into focused steps) ---------------------------------
def _book_seed_query() -> str:
    """
    Keep the exact query string used previously.
    """
    return "python development"


def _book_seed_limit() -> int:
    """
    Keep the exact limit used previously.
    """
    return 10


async def _create_book_service() -> BookService:
    """
    Create a BookService with a fresh async session each time (as before).
    """
    session = AsyncSessionLocal()
    # Note: we pass the session ownership to the service; context-managed in caller.
    return BookService(session)


async def _seed_books_via_service(service: BookService, query: str, limit: int) -> bool:
    """
    Execute the seeding via Google through the service; return success flag.
    """
    return await service.seed_from_google(query=query, limit=limit)


async def seed_books() -> None:
    """
    Orchestrate book seeding with the same query & limit, same branching/logging.
    """
    async with AsyncSessionLocal() as session:
        service = BookService(session)
        did_seed = await _seed_books_via_service(
            service, query=_book_seed_query(), limit=_book_seed_limit()
        )
        if did_seed:
            logger.info("Books seeded successfully.")
        else:
            logger.info("No books found, skipping book seeding.")


# --- Startup orchestration ---------------------------------------------------
async def _run_startup_steps() -> None:
    """
    Keep the original order exactly: init DB -> seed users -> seed books.
    """
    await init_db()
    await seed_users()
    await seed_books()


@app.on_event("startup")
async def on_startup() -> None:
    """FastAPI startup hook."""
    await _run_startup_steps()
    logger.info("Application startup complete.")
