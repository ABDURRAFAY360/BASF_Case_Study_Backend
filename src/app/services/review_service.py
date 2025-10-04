from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.repositories.review_repo import ReviewRepository
from app.repositories.book_repo import BookRepository
from app.schemas.review import ReviewUpsertRequest, ReviewRead


class ReviewService:
    def __init__(self, session: AsyncSession):
        self.reviews = ReviewRepository(session)
        self.books = BookRepository(session)

    async def upsert(
        self, *, book_id: int, username: str, data: ReviewUpsertRequest
    ) -> ReviewRead:
        if not await self.books.get(book_id):
            raise HTTPException(status_code=404, detail="Book not found")
        saved = await self.reviews.upsert(
            book_id=book_id,
            username=username,
            rating=data.rating,
            review_text=data.review_text,
        )
        return ReviewRead.model_validate(saved)

    async def list_for_book(self, *, book_id: int) -> list[ReviewRead]:
        if not await self.books.get(book_id):
            raise HTTPException(status_code=404, detail="Book not found")
        return [
            ReviewRead.model_validate(x) for x in await self.reviews.for_book(book_id)
        ]
