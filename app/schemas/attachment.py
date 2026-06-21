from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class AttachmentRead(BaseModel):
    id: int
    original_filename: str
    file_size: int
    created_at: datetime
    
    # Compatibility fields populated automatically from model properties/columns
    filename: Optional[str] = None
    unique_filename: Optional[str] = None
    mime_type: Optional[str] = None
    note_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
