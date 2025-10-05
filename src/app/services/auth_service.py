from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repo import UserRepository
from app.core.security import create_access_token


class AuthUseCases:
    """
    Handles authentication-related business logic.
    This refactor keeps the same behavior — just more modular and readable.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.users = UserRepository(db)

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------
    async def login(self, username: str, password: str) -> str:
        """
        Validate user credentials and return a JWT access token.

        Raises:
            HTTPException(401) if credentials are invalid.
        """
        if not await self._is_valid_user(username, password):
            self._raise_invalid_credentials()

        return self._generate_access_token(username)

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    async def _is_valid_user(self, username: str, password: str) -> bool:
        """Check user credentials through the repository."""
        return await self.users.validate_credentials(username, password)

    @staticmethod
    def _raise_invalid_credentials() -> None:
        """Raise a consistent unauthorized error (kept identical in meaning)."""
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    @staticmethod
    def _generate_access_token(username: str) -> str:
        """Generate a JWT token for the given username."""
        return create_access_token(username)
