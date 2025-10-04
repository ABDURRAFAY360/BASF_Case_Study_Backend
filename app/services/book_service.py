from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.book_repo import BookRepository
from app.repositories.review_repo import ReviewRepository
from app.schemas.book import BookRead

class BookService:
    def __init__(self, session: AsyncSession):
        self.books = BookRepository(session)
        self.reviews = ReviewRepository(session)

    async def list_books(self, *, search: str, limit: int, offset: int) -> list[BookRead]:
        rows = await self.books.list_with_avg(search=search, limit=limit, offset=offset)
        out: list[BookRead] = []
        for row in rows:
            book = row["book"]                # the Book object
            avg = row["average_rating"]       # the float/None

            out.append(
                BookRead(
                    title=book.title,
                    author=book.author,
                    genre=book.genre,
                    average_rating=(float(avg) if avg is not None else None),
                )
            )
        return out
    async def seed_if_needed(self, books: list[dict]) -> None:
        await self.books.seed_if_empty(books)
