from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import exists

from app.models.user import User
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    """
    User repository specializing in user-related database operations.
    """
    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """
        Retrieves a user by their unique email address.
        """
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def check_email_exists(self, db: AsyncSession, email: str) -> bool:
        """
        Checks if a user email already exists in the system.
        Uses a highly optimized SQL EXISTS query to minimize DB lookup overhead.
        """
        query = select(exists().where(User.email == email))
        result = await db.execute(query)
        return bool(result.scalar())

user_repository = UserRepository()
