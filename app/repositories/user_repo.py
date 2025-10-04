from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.core.security import verify_password

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def validate_credentials(self, username: str, password: str) -> bool:
        user = await self.get_by_username(username)
        print("userxxxxx:", user)
        if not user or not verify_password(password, user.password):
            return False
        return True
        
    async def get_by_username(self, username: str) -> User:
        stmt = select(User).where(User.username == username).limit(1)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def bulk_upsert(self, users: list[dict]) -> int:
        if not users:
            return 0

        # Get all usernames in this batch
        usernames = [user["username"] for user in users]

        # Fetch existing users in a single query
        stmt = select(User.username).where(User.username.in_(usernames))
        result = await self.session.execute(stmt)
        existing_usernames = {row[0] for row in result.fetchall()}

        # Prepare only new users
        new_users = [User(**user) for user in users if user["username"] not in existing_usernames]

        # Bulk add new users
        if new_users:
            self.session.add_all(new_users)
            await self.session.commit()

        return len(new_users)