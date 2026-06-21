from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from sqlalchemy.orm import selectinload

from app.models.note import Note
from app.repositories.base import BaseRepository

class NoteRepository(BaseRepository[Note]):
    """
    Note repository encapsulating query methods for notes operations.
    Encapsulates pagination, search, and relationship preloading.
    """
    def __init__(self):
        super().__init__(Note)

    async def get_by_user(
        self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100, search: Optional[str] = None
    ) -> List[Note]:
        """
        Retrieves all notes owned by a specific user with offset pagination.
        Supports case-insensitive search filtering across titles and content.
        Preloads note attachments using 'selectinload' to prevent downstream async lazy-loading errors.
        """
        query = select(Note).where(Note.user_id == user_id).options(selectinload(Note.attachments))
        if search:
            search_filter = f"%{search}%"
            query = query.where(
                or_(
                    Note.title.ilike(search_filter),
                    Note.content.ilike(search_filter)
                )
            )
        # Orders notes by recently updated/created first
        query = query.order_by(Note.updated_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_for_user(self, db: AsyncSession, *, note_id: int, user_id: int) -> Optional[Note]:
        """
        Retrieves a single note by its ID, validating user ownership in the SQL query layer.
        Preloads note attachments using 'selectinload'.
        """
        query = (
            select(Note)
            .where(Note.id == note_id, Note.user_id == user_id)
            .options(selectinload(Note.attachments))
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

note_repository = NoteRepository()
