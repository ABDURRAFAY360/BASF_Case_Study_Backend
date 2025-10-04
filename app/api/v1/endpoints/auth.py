from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import AuthUseCases
from app.db.session import get_session
from app.models.user import User
from sqlalchemy import select


router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_session)) -> TokenResponse:
    token = await AuthUseCases(db).login(payload.username, payload.password)
    return TokenResponse(access_token=token)

@router.get("/debug-users")
async def debug_users(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(User))
    return result.scalars().all()