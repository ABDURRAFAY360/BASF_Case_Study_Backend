from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.models.review import Review

class ReviewRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert(self, *, book_id: int, username: str, rating: int, review_text: str) -> Review:
        stmt: Select = select(Review).where(Review.book_id == book_id, Review.username == username)
        existing = (await self.session.execute(stmt)).scalars().first()
        if existing:
            existing.rating = rating
            existing.review_text = review_text
            self.session.add(existing)
            await self.session.commit()
            await self.session.refresh(existing)
            return existing
        review = Review(book_id=book_id, username=username, rating=rating, review_text=review_text)
        self.session.add(review)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            existing = (await self.session.execute(stmt)).scalars().first()
            if existing:
                existing.rating = rating
                existing.review_text = review_text
                self.session.add(existing)
                await self.session.commit()
                await self.session.refresh(existing)
                return existing
            raise
        await self.session.refresh(review)
        return review

    async def for_book(self, book_id: int) -> list[Review]:
        res = await self.session.execute(
            select(Review).where(Review.book_id == book_id).order_by(Review.created_at.desc())
        )
        return list(res.scalars().all())
