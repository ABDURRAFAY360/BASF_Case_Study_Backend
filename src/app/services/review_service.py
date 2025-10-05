from __future__ import annotations

from typing import Any, Iterable, List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.review_repo import ReviewRepository
from app.repositories.book_repo import BookRepository
from app.schemas.review import ReviewUpsertRequest, ReviewRead


class ReviewService:
    """
    Service layer for book reviews.
    Logic is unchanged; code is just decomposed and documented.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.reviews = ReviewRepository(session)
        self.books = BookRepository(session)

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------
    async def upsert(
        self, *, book_id: int, username: str, data: ReviewUpsertRequest
    ) -> ReviewRead:
        """
        Create or update a review for a given book and user.
        - 404 if the book does not exist (kept identical).
        """
        await self._ensure_book_exists(book_id)

        saved = await self._save_review(
            book_id=book_id,
            username=username,
            rating=data.rating,
            review_text=data.review_text,
        )
        return self._to_review_read(saved)

    async def list_for_book(self, *, book_id: int) -> list[ReviewRead]:
        """
        List all reviews for a given book.
        - 404 if the book does not exist (kept identical).
        """
        await self._ensure_book_exists(book_id)

        rows = await self.reviews.for_book(book_id)
        return self._to_review_reads(rows)

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    async def _ensure_book_exists(self, book_id: int) -> None:
        """
        Validate that the target book exists; raise the same 404 as original.
        """
        if not await self.books.get(book_id):
            self._raise_book_not_found()

    @staticmethod
    def _raise_book_not_found() -> None:
        """Raise a consistent 404 error (message unchanged)."""
        raise HTTPException(status_code=404, detail="Book not found")

    async def _save_review(
        self, *, book_id: int, username: str, rating: int, review_text: str | None
    ) -> Any:
        """Delegate persistence to the repository (behavior unchanged)."""
        return await self.reviews.upsert(
            book_id=book_id,
            username=username,
            rating=rating,
            review_text=review_text,
        )

    @staticmethod
    def _to_review_read(row: Any) -> ReviewRead:
        """Map a single row/object to `ReviewRead` exactly as before."""
        return ReviewRead.model_validate(row)

    def _to_review_reads(self, rows: Iterable[Any]) -> List[ReviewRead]:
        """Map an iterable of rows/objects to a list of `ReviewRead`."""
        return [self._to_review_read(x) for x in rows]
