from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.note import Note

class Attachment(Base):
    __tablename__ = "attachments"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # MIME Type tracked for proper HTTP download responses, defaulting to standard octet-stream
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False, default="application/octet-stream")
    
    note_id: Mapped[int] = mapped_column(ForeignKey("notes.id", ondelete="CASCADE"), nullable=False)
    
    # UTC Timestamp using database defaults or Python timezone defaults
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc)
    )
    
    # Relationships
    # Belongs to one Note
    note: Mapped["Note"] = relationship("Note", back_populates="attachments")

    # Getters and Setters for legacy properties to prevent codebase regression
    @property
    def filename(self) -> str:
        return self.original_filename

    @filename.setter
    def filename(self, value: str) -> None:
        self.original_filename = value

    @property
    def unique_filename(self) -> str:
        return self.stored_filename

    @unique_filename.setter
    def unique_filename(self, value: str) -> None:
        self.stored_filename = value
