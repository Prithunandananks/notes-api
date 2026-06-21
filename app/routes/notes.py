import os
from typing import List, Optional
from fastapi import APIRouter, Depends, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.schemas.note import NoteCreate, NoteUpdate, NoteRead
from app.schemas.attachment import AttachmentRead
from app.services.note import note_service

router = APIRouter(prefix="/notes", tags=["Notes"])

@router.get("", response_model=List[NoteRead], summary="List Notes")
async def list_notes(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lists notes owned by the authenticated active user with pagination and optional search filter.
    """
    return await note_service.get_notes(db, user_id=current_user.id, skip=skip, limit=limit, search=search)

@router.post("", response_model=NoteRead, status_code=status.HTTP_201_CREATED, summary="Create Note")
async def create_note(
    note_in: NoteCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Creates a new note for the authenticated active user.
    """
    return await note_service.create_note(db, note_in, user_id=current_user.id)

@router.get("/{note_id}", response_model=NoteRead, summary="Get Note")
async def get_note(
    note_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves note details by note ID, validating user ownership.
    """
    return await note_service.get_note_by_id(db, note_id=note_id, user_id=current_user.id)

@router.put("/{note_id}", response_model=NoteRead, summary="Update Note")
async def update_note(
    note_id: int,
    note_in: NoteUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Updates note title and/or content, validating user ownership.
    """
    return await note_service.update_note(db, note_id=note_id, note_in=note_in, user_id=current_user.id)

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Note")
async def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Deletes note and its attached files, validating user ownership.
    """
    await note_service.delete_note(db, note_id=note_id, user_id=current_user.id)
    return None

@router.post("/{note_id}/attachments", response_model=AttachmentRead, status_code=status.HTTP_201_CREATED, summary="Upload Note Attachment")
async def upload_attachment(
    note_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Uploads and links a file to a note, validating note ownership.
    Checks file types and sizes.
    """
    return await note_service.add_attachment(db, note_id=note_id, user_id=current_user.id, file=file)

@router.get("/{note_id}/attachments/{attachment_id}", summary="Download Note Attachment")
async def download_attachment(
    note_id: int,
    attachment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Downloads an attached file after validating user note ownership.
    """
    attachment = await note_service.get_attachment(
        db, note_id=note_id, attachment_id=attachment_id, user_id=current_user.id
    )
    if not os.path.exists(attachment.file_path):
        raise NotFoundException("Physical file not found on storage disk.")
        
    return FileResponse(
        path=attachment.file_path,
        filename=attachment.original_filename,
        media_type=attachment.mime_type
    )

@router.delete("/{note_id}/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Note Attachment")
async def delete_attachment(
    note_id: int,
    attachment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Deletes note attachment, purging it from disk and database, validating note ownership.
    """
    await note_service.delete_attachment(
        db, note_id=note_id, attachment_id=attachment_id, user_id=current_user.id
    )
    return None
