import os
import uuid
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import BadRequestException
from app.models.attachment import Attachment
from app.repositories.attachment import attachment_repository

class FileService:
    """
    File business logic service.
    Orchestrates physical file validation, local storage persistence, deletions,
    and database attachment metadata records.
    """
    async def validate_file(self, file: UploadFile) -> None:
        """
        Validates file size limits and file type extensions/mime types.
        Raises:
            BadRequestException: If file size exceeds configuration, or type is unsupported.
        """
        size = file.size
        if size is None:
            # Fallback read for size discovery if not populated by gateway
            content = await file.read()
            size = len(content)
            await file.seek(0)
            
        if size > settings.MAX_FILE_SIZE:
            raise BadRequestException(
                f"File size exceeds limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
            )
            
        filename = file.filename or ""
        ext = filename.split(".")[-1].lower() if "." in filename else ""
        if ext not in settings.ALLOWED_FILE_TYPES:
            raise BadRequestException(
                f"File type '.{ext}' is not supported. Supported: {', '.join(settings.ALLOWED_FILE_TYPES)}"
            )

    async def save_file_to_disk(self, file: UploadFile) -> tuple[str, str, str, int]:
        """
        Saves file to physical storage using generated UUID.
        Returns: (original_filename, stored_filename, file_path, file_size)
        """
        await self.validate_file(file)
        
        original_name = file.filename or "unknown"
        ext = original_name.split(".")[-1].lower() if "." in original_name else "bin"
        stored_name = f"{uuid.uuid4().hex}.{ext}"
        file_path = os.path.join(settings.UPLOAD_DIR, stored_name)
        
        try:
            # Save blocks chunk-by-chunk to prevent memory bloating
            with open(file_path, "wb") as buffer:
                await file.seek(0)
                while chunk := await file.read(1024 * 1024):  # 1MB chunks
                    buffer.write(chunk)
            file_size = os.path.getsize(file_path)
        except Exception as e:
            # Clean up partial files upon failure
            self.delete_file_from_disk(file_path)
            raise BadRequestException(f"Failed to persist file: {str(e)}")
            
        return original_name, stored_name, file_path, file_size

    def delete_file_from_disk(self, file_path: str) -> None:
        """
        Safely removes a file from physical storage.
        """
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                # Silently log errors in production logging
                pass

    async def create_attachment_metadata(
        self, db: AsyncSession, note_id: int, original_filename: str, stored_filename: str, file_path: str, file_size: int, mime_type: str
    ) -> Attachment:
        """
        Persists file metadata record in the attachments database table.
        """
        db_attachment = Attachment(
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type,
            note_id=note_id
        )
        return await attachment_repository.create(db, db_obj=db_attachment)

file_service = FileService()
