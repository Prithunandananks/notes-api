from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

from app.schemas.attachment import AttachmentRead

class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Title must be between 1 and 255 characters")
    content: str = Field(..., min_length=1, description="Content cannot be empty")

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Title must be between 1 and 255 characters")
    content: Optional[str] = Field(None, min_length=1, description="Content cannot be empty")

class NoteRead(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime
    attachments: List[AttachmentRead] = []
    
    # Compatibility fields populated automatically from model columns
    user_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
