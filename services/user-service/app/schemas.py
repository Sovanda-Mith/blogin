from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserProfileBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    display_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=500)


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(BaseModel):
    display_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=500)


class UserProfileResponse(UserProfileBase):
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserProfileWithEmail(UserProfileResponse):
    email: str
    is_active: bool


class APIResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    message: str
    errors: Optional[list] = None


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    limit: int
    total_pages: int
    has_next: bool
    has_prev: bool
