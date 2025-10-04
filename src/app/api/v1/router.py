from fastapi import APIRouter
from .endpoints import auth, book, review

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(book.router, prefix="/books", tags=["books"])
api_router.include_router(review.router, prefix="/reviews", tags=["reviews"])
