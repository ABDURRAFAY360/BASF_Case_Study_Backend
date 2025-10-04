from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repo import UserRepository
from app.core.security import create_access_token


class AuthUseCases:
    def __init__(self, db: AsyncSession):
        self.users = UserRepository(db)

    async def login(self, username: str, password: str) -> str:
        is_valid = await self.users.validate_credentials(username, password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )
        return create_access_token(username)
