from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import json
from sqlalchemy import Select, func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import setup_logger
from app.models.book import Book
from app.models.review import Review

logger = setup_logger(__name__)


class BookRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # -------------------------------------------------------------------------
    # Seeding
    # -------------------------------------------------------------------------
    async def seed_books(self, books: Optional[List[Dict[str, Any]]] = None) -> bool:
        """
        Seed books into the database. If 'books' is None or empty, try the seed file.
        Returns True if the method ran without hard failure (matching original intent).
        """
        rows = books if books else self._load_seed_file()
        if not rows:
            return False  # No data at all

        inserted = await self._insert_missing_books(rows)
        if inserted:
            await self.session.commit()
        return True

    def _load_seed_file(self) -> List[Dict[str, Any]]:
        """
        Load a JSON array of book rows from the configured seed file.
        Returns [] on any issue (missing file, bad JSON, wrong shape).
        """
        seed_path = Path(settings.BOOKS_SEED_FILE).resolve()
        if not seed_path.exists():
            return []

        try:
            data = json.loads(seed_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            # Keep logging lightweight and human-friendly.
            logger.error("Invalid JSON in seed file %s: %s", seed_path, exc)
            return []

        if not isinstance(data, list):
            logger.error("Seed file %s must contain a JSON array.", seed_path)
            return []

        return data

    async def _insert_missing_books(self, rows: Iterable[Dict[str, Any]]) -> int:
        """
        Insert rows that don't already exist (same title + author).
        Returns the count of rows added to the session.
        """
        inserted = 0
        for row in rows:
            title = row["title"]
            author = row["author"]

            if not await self._book_exists(title, author):
                self.session.add(Book(**row))
                inserted += 1

        return inserted

    async def _book_exists(self, title: str, author: str) -> bool:
        """
        Check if a book with the same (title, author) already exists.
        """
        stmt = select(Book).where(and_(Book.title == title, Book.author == author))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    # -------------------------------------------------------------------------
    # Listing with average rating
    # -------------------------------------------------------------------------
    async def list_with_avg(
        self, *, search: Optional[str] = None, limit: int = 10, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Return a list of dicts: {"book": Book, "average_rating": float|None}
        Ordered by title ASC, with optional case-insensitive search on title/author.
        """
        stmt = self._base_list_stmt(limit=limit, offset=offset)
        if search:
            stmt = self._apply_search_filter(stmt, search)

        result = await self.session.execute(stmt)
        return self._rows_to_book_avg_list(result.all())

    def _base_list_stmt(self, *, limit: int, offset: int) -> Select:
        """
        Build the base SELECT joining reviews (LEFT OUTER) and averaging ratings.
        """
        avg_rating = func.avg(Review.rating).label("average_rating")
        return (
            select(Book, avg_rating)
            .join(Review, Review.book_id == Book.id, isouter=True)
            .group_by(Book.id)
            .order_by(Book.title.asc())
            .limit(limit)
            .offset(offset)
        )

    def _apply_search_filter(self, stmt: Select, search: str) -> Select:
        """
        Apply a case-insensitive LIKE filter on title or author.
        """
        like_pattern = f"%{search.lower()}%"
        return stmt.where(
            func.lower(Book.title).like(like_pattern)
            | func.lower(Book.author).like(like_pattern)
        )

    @staticmethod
    def _rows_to_book_avg_list(rows: List[Any]) -> List[Dict[str, Any]]:
        """
        Convert SQLAlchemy row objects to the expected dict shape.
        """
        return [
            {"book": row.Book, "average_rating": row.average_rating} for row in rows
        ]

    # -------------------------------------------------------------------------
    # Single fetch
    # -------------------------------------------------------------------------
    async def get(self, book_id: int) -> Optional[Book]:
        """
        Fetch a book by primary key.
        """
        return await self.session.get(Book, book_id)
