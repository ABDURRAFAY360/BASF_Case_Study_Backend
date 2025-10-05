from sqlalchemy import String,UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Book(Base):
    __tablename__ = "books"
    __table_args__ = (UniqueConstraint("title", "author", name="uq_title_author"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    author: Mapped[str] = mapped_column(String(255), index=True)
    genre: Mapped[str] = mapped_column(String(100), index=True)
