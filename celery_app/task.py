import asyncio
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.clients.google_book_clients import GoogleBooksClient
from app.repositories.book_repo import BookRepository
from app.services.book_service import BookService
from . import celery_app

@celery_app.task(name="celery_app.tasks.refresh_books")
def refresh_books() -> int:
    if not settings.GOOGLE_BOOKS_ENABLED:
        return 0

    async def _run() -> int:
        async with AsyncSessionLocal() as session:
            book_service = BookService(session)
            await book_service.seed_from_google(settings.GOOGLE_BOOKS_DEFAULT_QUERY, settings.GOOGLE_BOOKS_MAX_RESULTS)

    return asyncio.get_event_loop().run_until_complete(_run())
