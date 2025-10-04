from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_username
from app.schemas.book import BookRead
from app.services.book_service import BookService

router = APIRouter(dependencies=[Depends(get_current_username)])

@router.get("/", response_model=list[BookRead])
async def list_books(
    search: str  = Query(default=None, description="Search by title or author"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> list[BookRead]:
    return await BookService(db).list_books(search=search, limit=limit, offset=offset)
