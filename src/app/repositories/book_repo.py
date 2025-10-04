from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.book import Book
from app.models.review import Review
from typing import Optional, List, Dict
import json
from pathlib import Path
from app.core.config import settings


class BookRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def seed_books(self, books: List[Dict] = None) -> bool:
        rows = books
        # Load from seed file if no books were passed
        if not rows:
            seed_path = Path(settings.BOOKS_SEED_FILE).resolve()
            if not seed_path.exists():
                return False  # No file, nothing to seed
            try:
                rows = json.loads(seed_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                # Log the error in production
                print(f"Invalid JSON in seed file: {e}")
                return False
        if not rows:
            return False  # No data at all
        # Insert into DB
        self.session.add_all([Book(**b) for b in rows])
        await self.session.commit()
        return True

    async def list_with_avg(
        self,
        *,
        search: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List[Dict]:
        avg_rating = func.avg(Review.rating).label("average_rating")

        # Base query
        stmt: Select = (
            select(Book, avg_rating)
            .join(Review, Review.book_id == Book.id, isouter=True)
            .group_by(Book.id)
            .order_by(Book.title.asc())
            .limit(limit)
            .offset(offset)
        )

        # Optional search filter
        if search:
            like_pattern = f"%{search.lower()}%"
            stmt = stmt.where(
                func.lower(Book.title).like(like_pattern)
                | func.lower(Book.author).like(like_pattern)
            )

        # Execute query
        result = await self.session.execute(stmt)

        # Convert rows into structured list
        return [
            {"book": row.Book, "average_rating": row.average_rating}
            for row in result.all()
        ]

    async def get(self, book_id: int) -> Book:
        return await self.session.get(Book, book_id)
