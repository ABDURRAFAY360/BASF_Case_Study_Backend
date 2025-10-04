from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
import json

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine, AsyncSessionLocal
from app.repositories.user_repo import UserRepository
from app.repositories.book_repo import BookRepository
from app.core.security import hash_password

app = FastAPI(title=settings.PROJECT_NAME,
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
@app.on_event("startup")
async def on_startup() -> None:
    # Create schema
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed users if empty
    async with AsyncSessionLocal() as session:
        print("Seeding users...")
        repo = UserRepository(session)
        seed_path = Path(settings.USERS_SEED_FILE).resolve()
        print("seed_path:", seed_path)
        if seed_path.exists():
            rows = json.loads(seed_path.read_text())
            print("rows:", rows)
            to_insert = [
                {
                    "username": row["username"],
                    "password": hash_password(row["password"]),
                }
                for row in rows
            ]
            print("to_insert:", to_insert)
            await repo.bulk_upsert(to_insert)
        else:
            print("No user seed file found, skipping user seeding.")

@app.on_event("startup")
async def on_startup() -> None:
    # Create schema
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Seed books if empty
    async with AsyncSessionLocal() as session:
        repo = BookRepository(session)
        seed_path = Path(settings.BOOKS_SEED_FILE).resolve()
        print("seed_path:", seed_path)
        if seed_path.exists():
            rows = json.loads(seed_path.read_text())
            print("rows:", rows)
            await repo.seed_books(rows)
        else:
            print("No book seed file found, skipping book seeding.")
       
        
app.include_router(api_router, prefix=settings.API_V1_STR)

