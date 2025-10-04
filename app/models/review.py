from datetime import datetime
from sqlalchemy import ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint("book_id", "username", name="uq_book_user"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"), index=True
    )
    username: Mapped[str] = mapped_column(String(100), index=True)
    rating: Mapped[int] = mapped_column()
    review_text: Mapped[str] = mapped_column(String(2048))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
