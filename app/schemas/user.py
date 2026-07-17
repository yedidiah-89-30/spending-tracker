from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)


class UserRead(UserBase):
    """What we return to clients - never includes hashed_password."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    currency: str
    is_active: bool
    created_at: datetime
