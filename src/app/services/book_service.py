from __future__ import annotations

from typing import Any, Iterable, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.book_repo import BookRepository
from app.repositories.review_repo import ReviewRepository
from app.schemas.book import BookRead
from app.clients.google_book_clients import GoogleBooksClient
from app.core.logging import setup_logger

logger = setup_logger(__name__)


class BookService:
    """
    Thin service layer coordinating repositories and external clients.
    All public methods preserve the original behavior.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.books = BookRepository(session)
        self.reviews = ReviewRepository(session)

    # -------------------------------------------------------------------------
    # List books
    # -------------------------------------------------------------------------
    async def list_books(
        self, *, search: str, limit: int, offset: int
    ) -> list[BookRead]:
        """
        Return a paginated list of books enriched with their average rating.
        (Behavior unchanged: same repo call, same mapping semantics.)
        """
        rows = await self.books.list_with_avg(search=search, limit=limit, offset=offset)
        return self._rows_to_book_reads(rows)

    def _rows_to_book_reads(self, rows: Iterable[dict[str, Any]]) -> list[BookRead]:
        """
        Convert repository rows into `BookRead` models.
        Each row is expected to have keys: 'book' and 'average_rating'.
        """
        out: list[BookRead] = []
        for row in rows:
            out.append(self._row_to_book_read(row))
        return out

    def _row_to_book_read(self, row: dict[str, Any]) -> BookRead:
        """Map a single row to `BookRead`, preserving the original casting rules."""
        book = row["book"]  # ORM Book object
        avg = row["average_rating"]  # float | None
        return BookRead(
            title=book.title,
            author=book.author,
            genre=book.genre,
            average_rating=self._to_optional_float(avg),
        )

    @staticmethod
    def _to_optional_float(value: Any) -> float | None:
        """Cast rating to float if present; otherwise None (unchanged semantics)."""
        return float(value) if value is not None else None

    # -------------------------------------------------------------------------
    # Seed from Google
    # -------------------------------------------------------------------------
    async def seed_from_google(
        self, query: str = "python programming", limit: int = 20
    ) -> bool:
        """
        Fetch books from Google Books API and seed them into DB.

        Returns:
            True if successful, False if any error occurs or nothing fetched.
        """
        # NOTE: Keep client creation outside the try-block to preserve original behavior.
        client = self._new_google_client()

        try:
            fetched_books = await self._fetch_books(client, query=query, limit=limit)
            if not fetched_books:
                logger.warning(
                    "No books fetched from Google Books API for query='%s'", query
                )
                return False

            await self._seed_books_in_repo(fetched_books)
            logger.info(
                "Seeded %d books from Google API for query='%s'",
                len(fetched_books),
                query,
            )
            return True

        except Exception as e:  # noqa: BLE001 – preserve original broad exception handling
            logger.exception("Failed to seed books from Google API: %s", e)
            return False

        finally:
            # Always close the client as in the original code.
            await client.close()

    # -- helpers for seeding ---------------------------------------------------
    def _new_google_client(self) -> GoogleBooksClient:
        """Create a new Google Books API client (isolated for clarity/testing)."""
        return GoogleBooksClient()

    async def _fetch_books(
        self, client: GoogleBooksClient, *, query: str, limit: int
    ) -> List[Any]:
        """Fetch raw book payloads from Google Books API."""
        return await client.search_books(query=query, max_results=limit)

    async def _seed_books_in_repo(self, books_payload: Iterable[Any]) -> None:
        """Insert/merge fetched books via the repository (behavior unchanged)."""
        await self.books.seed_books(books_payload)
