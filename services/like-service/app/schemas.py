from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class LikeBase(BaseModel):
    post_slug: str


class LikeCreate(LikeBase):
    pass


class LikeResponse(BaseModel):
    id: UUID
    post_id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class LikeCountResponse(BaseModel):
    post_slug: str
    count: int


class LikeStatusResponse(BaseModel):
    post_slug: str
    liked: bool


class APIResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    message: str
    errors: Optional[list] = None
