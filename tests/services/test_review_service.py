import pytest
from app.repositories.book_repo import BookRepository
from app.services.review_service import ReviewService
from app.schemas.review import ReviewUpsertRequest
from app.db.session import AsyncSessionLocal

@pytest.mark.asyncio
async def test_upsert_review_and_list():
    async with AsyncSessionLocal() as db:
        await BookRepository(db).seed_books([{"title":"T1","author":"A1","genre":"G"}])
        svc = ReviewService(db)
        r1 = await svc.upsert(book_id=1, username="abdur", data=ReviewUpsertRequest(rating=5, review_text="Great"))
        assert r1.rating == 5
        r2 = await svc.upsert(book_id=1, username="abdur", data=ReviewUpsertRequest(rating=3, review_text="Ok"))
        assert r2.rating == 3
        reviews = await svc.list_for_book(book_id=1)
        assert len(reviews) == 1 and reviews[0].username == "abdur"
