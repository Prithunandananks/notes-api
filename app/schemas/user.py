from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")

class UserLogin(UserBase):
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")

class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    # Config to read SQLAlchemy models natively
    model_config = ConfigDict(from_attributes=True)
