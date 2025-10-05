from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.security import verify_password
from app.core.logging import setup_logger

logger = setup_logger(__name__)


class UserRepository:
    """
    Data access for User entities.
    Behavior preserved; code split into small, readable helpers.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # -------------------------------------------------------------------------
    # Auth helpers
    # -------------------------------------------------------------------------
    async def validate_credentials(self, username: str, password: str) -> bool:
        """
        Return True iff the user exists and the password is valid.
        """
        user = await self.get_by_username(username)
        # No extra branching or side effects; same truth table as original.
        return bool(user and verify_password(password, user.password))

    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Fetch a single user by username (or None).
        """
        stmt = self._select_user_by_username_stmt(username)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    @staticmethod
    def _select_user_by_username_stmt(username: str):
        """Small helper to build the username lookup query."""
        return select(User).where(User.username == username).limit(1)

    # -------------------------------------------------------------------------
    # Bulk upsert (insert-only for non-existing usernames)
    # -------------------------------------------------------------------------
    async def bulk_upsert(self, users: List[Dict[str, Any]]) -> int:
        """
        Insert users that don't already exist.
        Returns the count of newly inserted users.
        """
        if not users:
            return 0

        usernames = self._extract_usernames(users)
        existing_usernames = await self._fetch_existing_usernames(usernames)
        new_users = self._filter_new_users(users, existing_usernames)

        if new_users:
            await self._bulk_insert(new_users)

        return len(new_users)

    # -- internal pieces -------------------------------------------------------
    @staticmethod
    def _extract_usernames(users: Iterable[Dict[str, Any]]) -> List[str]:
        """Pull the username field from each payload (assumes valid input)."""
        return [user["username"] for user in users]

    async def _fetch_existing_usernames(self, usernames: Iterable[str]) -> set[str]:
        """
        Fetch existing usernames from the DB in a single query.
        """
        stmt = select(User.username).where(User.username.in_(list(usernames)))
        result = await self.session.execute(stmt)
        return {row[0] for row in result.fetchall()}

    @staticmethod
    def _filter_new_users(
        users: Iterable[Dict[str, Any]], existing_usernames: set[str]
    ) -> List[User]:
        """
        Build ORM User objects only for usernames not present already.
        """
        return [
            User(**payload)
            for payload in users
            if payload["username"] not in existing_usernames
        ]

    async def _bulk_insert(self, users: List[User]) -> None:
        """
        Add and commit a batch of new users.
        """
        self.session.add_all(users)
        await self.session.commit()
