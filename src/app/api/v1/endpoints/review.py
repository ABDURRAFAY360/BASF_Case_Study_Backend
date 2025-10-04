from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_username
from app.schemas.review import ReviewUpsertRequest, ReviewRead
from app.services.review_service import ReviewService

router = APIRouter(dependencies=[Depends(get_current_username)])


@router.post("/{book_id}/reviews", response_model=ReviewRead)
async def upsert_review(
    book_id: int,
    payload: ReviewUpsertRequest,
    db: AsyncSession = Depends(get_db),
    username: str = Depends(get_current_username),
) -> ReviewRead:
    return await ReviewService(db).upsert(
        book_id=book_id, username=username, data=payload
    )


@router.get("/{book_id}/reviews", response_model=list[ReviewRead])
async def list_reviews(
    book_id: int, db: AsyncSession = Depends(get_db)
) -> list[ReviewRead]:
    return await ReviewService(db).list_for_book(book_id=book_id)
