from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.book_repo import BookRepository
from app.repositories.review_repo import ReviewRepository
from app.schemas.book import BookRead
from app.clients.google_book_clients import GoogleBooksClient
from app.core.logging import setup_logger

logger = setup_logger(__name__)

class BookService:
    def __init__(self, session: AsyncSession):
        self.books = BookRepository(session)
        self.reviews = ReviewRepository(session)

    async def list_books(
        self, *, search: str, limit: int, offset: int
    ) -> list[BookRead]:
        rows = await self.books.list_with_avg(search=search, limit=limit, offset=offset)
        out: list[BookRead] = []
        for row in rows:
            book = row["book"]  # the Book object
            avg = row["average_rating"]  # the float/None

            out.append(
                BookRead(
                    title=book.title,
                    author=book.author,
                    genre=book.genre,
                    average_rating=(float(avg) if avg is not None else None),
                )
            )
        return out
    
    async def seed_from_google(self, query: str = "python programming", limit: int = 20) -> bool:
        """Fetch books from Google Books API and seed them into DB.
        Returns:
            True if successful, False if any error occurs.
        """
        client = GoogleBooksClient()
        try:
            fetched_books = await client.search_books(query=query, max_results=limit)
            if not fetched_books:
                logger.warning("No books fetched from Google Books API for query='%s'", query)
                return False

            await self.books.seed_books(fetched_books)
            logger.info("Seeded %d books from Google API for query='%s'", len(fetched_books), query)
            return True

        except Exception as e:
            logger.exception("Failed to seed books from Google API: %s", e)
            return False

        finally:
            await client.close()