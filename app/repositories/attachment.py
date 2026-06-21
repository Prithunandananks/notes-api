from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.attachment import Attachment
from app.models.note import Note
from app.repositories.base import BaseRepository

class AttachmentRepository(BaseRepository[Attachment]):
    """
    Attachment repository specializing in note attachment operations.
    """
    def __init__(self):
        super().__init__(Attachment)

    async def get_by_note(self, db: AsyncSession, *, note_id: int) -> List[Attachment]:
        """
        Retrieves all database metadata records for attachments belonging to a specific note.
        """
        query = select(Attachment).where(Attachment.note_id == note_id)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_by_id_and_user(self, db: AsyncSession, *, attachment_id: int, user_id: int) -> Optional[Attachment]:
        """
        Retrieves a file attachment by its ID, ensuring the parent note is owned by the user.
        Uses a SQL JOIN clause to handle tenancy checking directly at the database layer.
        """
        query = (
            select(Attachment)
            .join(Note)
            .where(Attachment.id == attachment_id, Note.user_id == user_id)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

attachment_repository = AttachmentRepository()
