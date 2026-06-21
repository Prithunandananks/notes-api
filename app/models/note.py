from datetime import datetime, timezone
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.attachment import Attachment

class Note(Base):
    __tablename__ = "notes"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # UTC Timestamps using database defaults or Python timezone defaults
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        default=lambda: datetime.now(timezone.utc)
    )
    
    # Relationships
    # Belongs to one User
    user: Mapped["User"] = relationship("User", back_populates="notes")
    
    # One Note has many attachments, cascade deletes physical file references on database delete
    attachments: Mapped[List["Attachment"]] = relationship(
        "Attachment", 
        back_populates="note", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )
