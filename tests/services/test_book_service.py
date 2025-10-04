import pytest
from app.services.book_service import BookService
from app.repositories.book_repo import BookRepository
from app.db.session import AsyncSessionLocal

@pytest.mark.asyncio
async def test_list_books_empty():
    async with AsyncSessionLocal() as db:
        assert await BookService(db).list_books(search=None, limit=10, offset=0) == []

@pytest.mark.asyncio
async def test_seed_and_search():
    async with AsyncSessionLocal() as db:
        await BookRepository(db).seed_books([
            {"title":"T1","author":"A1","genre":"G"},
            {"title":"T2","author":"A2","genre":"G"}
        ])
        res = await BookService(db).list_books(search="T1", limit=10, offset=0)
        assert len(res) == 1 and res[0].title == "T1"
