from typing import List, Optional
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.note import Note
from app.models.attachment import Attachment
from app.repositories.note import note_repository
from app.repositories.attachment import attachment_repository
from app.schemas.note import NoteCreate, NoteUpdate
from app.services.file import file_service

class NoteService:
    """
    Note business logic service.
    Orchestrates Note CRUD operations, tenancy authorization checks, and attachment integrations.
    """
    async def create_note(self, db: AsyncSession, note_in: NoteCreate, user_id: int) -> Note:
        """
        Creates a new note associated with the authenticated user ID.
        """
        db_note = Note(
            title=note_in.title,
            content=note_in.content,
            user_id=user_id,
            attachments=[]
        )
        await note_repository.create(db, db_obj=db_note)
        # Fetch auto-generated timestamps and IDs before returning
        await db.refresh(db_note, attribute_names=["id", "created_at", "updated_at"])
        return db_note

    async def get_notes(
        self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100, search: Optional[str] = None
    ) -> List[Note]:
        """
        Retrieves notes belonging to the user with pagination and keyword search support.
        """
        return await note_repository.get_by_user(db, user_id=user_id, skip=skip, limit=limit, search=search)

    async def get_note_by_id(self, db: AsyncSession, note_id: int, user_id: int) -> Note:
        """
        Retrieves note details by ID, validating user ownership at the database layer.
        Raises:
            NotFoundException: If the note does not exist or user doesn't own it.
        """
        note = await note_repository.get_for_user(db, note_id=note_id, user_id=user_id)
        if not note:
            raise NotFoundException("Note not found or access denied.")
        return note

    async def update_note(self, db: AsyncSession, note_id: int, note_in: NoteUpdate, user_id: int) -> Note:
        """
        Updates an existing note, verifying ownership first.
        """
        note = await self.get_note_by_id(db, note_id=note_id, user_id=user_id)
        await note_repository.update(db, db_obj=note, obj_in=note_in)
        # Refresh server-managed updated_at field
        await db.refresh(note, attribute_names=["updated_at"])
        return note

    async def delete_note(self, db: AsyncSession, note_id: int, user_id: int) -> None:
        """
        Deletes a note, purges associated file attachments database metadata and disk files.
        """
        note = await self.get_note_by_id(db, note_id=note_id, user_id=user_id)
        
        # Cache disk file paths to clean up local storage upon successful db delete
        file_paths = [att.file_path for att in note.attachments]
        
        await note_repository.delete(db, db_obj=note)
        
        # Purge files from physical storage
        for path in file_paths:
            file_service.delete_file_from_disk(path)

    async def add_attachment(self, db: AsyncSession, note_id: int, user_id: int, file: UploadFile) -> Attachment:
        """
        Uploads and attaches a file to a note, validating note ownership.
        """
        # Throws exception if note doesn't exist or is owned by another user
        await self.get_note_by_id(db, note_id=note_id, user_id=user_id)
        
        # Save physical file to disk
        original_name, stored_name, file_path, file_size = await file_service.save_file_to_disk(file)
        
        # Save file attachment record to database
        try:
            return await file_service.create_attachment_metadata(
                db,
                note_id=note_id,
                original_filename=original_name,
                stored_filename=stored_name,
                file_path=file_path,
                file_size=file_size,
                mime_type=file.content_type or "application/octet-stream"
            )
        except Exception:
            file_service.delete_file_from_disk(file_path)
            raise

    async def delete_attachment(self, db: AsyncSession, note_id: int, attachment_id: int, user_id: int) -> None:
        """
        Deletes a specific note attachment, purging it from database metadata and disk storage.
        """
        # Validate note ownership
        await self.get_note_by_id(db, note_id=note_id, user_id=user_id)
        
        # Retrieve attachment verifying it belongs to note owned by user
        attachment = await attachment_repository.get_by_id_and_user(db, attachment_id=attachment_id, user_id=user_id)
        if not attachment or attachment.note_id != note_id:
            raise NotFoundException("Attachment not found or access denied.")
            
        file_path = attachment.file_path
        await attachment_repository.delete(db, db_obj=attachment)
        
        # Purge physical file from disk storage
        file_service.delete_file_from_disk(file_path)

    async def get_attachment(self, db: AsyncSession, note_id: int, attachment_id: int, user_id: int) -> Attachment:
        """
        Retrieves a note attachment by its ID, validating user note ownership first.
        Raises:
            NotFoundException: If the attachment does not exist or user doesn't own the note.
        """
        await self.get_note_by_id(db, note_id=note_id, user_id=user_id)
        attachment = await attachment_repository.get_by_id_and_user(db, attachment_id=attachment_id, user_id=user_id)
        if not attachment or attachment.note_id != note_id:
            raise NotFoundException("Attachment not found or access denied.")
        return attachment

note_service = NoteService()
