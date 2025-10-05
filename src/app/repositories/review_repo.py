from __future__ import annotations

from typing import Optional, List

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.review import Review


class ReviewRepository:
    """
    Data access for Review entities.
    Behavior is unchanged; code is decomposed for clarity and testability.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------
    async def upsert(
        self, *, book_id: int, username: str, rating: int, review_text: str
    ) -> Review:
        """
        Create/update a user's review for a given book.

        Logic preserved:
        1) Try to find an existing (book_id, username) review and update it.
        2) Otherwise insert a new review.
        3) If insert hits IntegrityError (race), reload existing and update it.
        """
        stmt = self._select_user_review_stmt(book_id=book_id, username=username)

        existing = await self._find_existing(stmt)
        if existing:
            self._apply_updates(existing, rating=rating, review_text=review_text)
            return await self._commit_and_refresh(existing)

        # No existing review: attempt insert
        new_review = self._build_new_review(
            book_id=book_id, username=username, rating=rating, review_text=review_text
        )
        self.session.add(new_review)

        try:
            await self.session.commit()
        except IntegrityError:
            # Race condition: someone inserted concurrently. Roll back and update.
            await self.session.rollback()
            return await self._handle_integrity_race(
                stmt=stmt, rating=rating, review_text=review_text
            )

        await self.session.refresh(new_review)
        return new_review

    async def for_book(self, book_id: int) -> List[Review]:
        """
        Return all reviews for a book, newest first (created_at DESC).
        """
        res = await self.session.execute(
            select(Review)
            .where(Review.book_id == book_id)
            .order_by(Review.created_at.desc())
        )
        return list(res.scalars().all())

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    @staticmethod
    def _select_user_review_stmt(*, book_id: int, username: str) -> Select:
        """Query for a user's review on a specific book."""
        return select(Review).where(
            Review.book_id == book_id,
            Review.username == username,
        )

    async def _find_existing(self, stmt: Select) -> Optional[Review]:
        """Execute statement and return first matching Review or None."""
        result = await self.session.execute(stmt)
        return result.scalars().first()

    @staticmethod
    def _apply_updates(review: Review, *, rating: int, review_text: str) -> None:
        """Mutate existing review fields (no extra validation to preserve behavior)."""
        review.rating = rating
        review.review_text = review_text

    async def _commit_and_refresh(self, review: Review) -> Review:
        """Commit current transaction and refresh the instance."""
        self.session.add(review)
        await self.session.commit()
        await self.session.refresh(review)
        return review

    @staticmethod
    def _build_new_review(
        *, book_id: int, username: str, rating: int, review_text: str
    ) -> Review:
        """Construct a new Review instance."""
        return Review(
            book_id=book_id,
            username=username,
            rating=rating,
            review_text=review_text,
        )

    async def _handle_integrity_race(
        self, *, stmt: Select, rating: int, review_text: str
    ) -> Review:
        """
        Handle concurrent insert race:
        - Re-select existing, update, commit, refresh.
        - If still not found, re-raise (same as original behavior).
        """
        existing = await self._find_existing(stmt)
        if not existing:
            # Preserve the original control flow: bubble up IntegrityError if truly unexpected.
            raise

        self._apply_updates(existing, rating=rating, review_text=review_text)
        return await self._commit_and_refresh(existing)
