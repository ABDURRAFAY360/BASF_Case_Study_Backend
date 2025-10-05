import asyncio
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.clients.google_book_clients import GoogleBooksClient
from app.repositories.book_repo import BookRepository
from app.services.book_service import BookService
from celery import shared_task
from app.core.logging import setup_logger

logger = setup_logger(__name__)

@shared_task(name="app.task.books.refresh_books")
def refresh_books() -> int:
    if not settings.GOOGLE_BOOKS_ENABLED:
        return 0

    async def _run() -> int:
        async with AsyncSessionLocal() as session:
            book_service = BookService(session)
            ok = await book_service.seed_from_google(settings.GOOGLE_BOOKS_DEFAULT_QUERY, settings.GOOGLE_BOOKS_MAX_RESULTS)
            return {"ok": ok, "query": settings.GOOGLE_BOOKS_DEFAULT_QUERY, "limit": settings.GOOGLE_BOOKS_MAX_RESULTS}
    try:
        result = asyncio.run(_run())
        logger.info("refresh_books finished: %s", result)
        return result
    except Exception as e:
        logger.exception("refresh_books failed: %s", e)
        return {"ok": False, "query": settings.GOOGLE_BOOKS_DEFAULT_QUERY, "limit": settings.GOOGLE_BOOKS_MAX_RESULTS, "error": str(e)}
