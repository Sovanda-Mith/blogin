from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: UUID
    slug: str
    created_at: datetime

    class Config:
        from_attributes = True


class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    summary: Optional[str] = Field(None, max_length=500)
    status: str = Field("published", pattern="^(draft|published|archived)$")
    tags: Optional[List[str]] = []


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    summary: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(None, pattern="^(draft|published|archived)$")
    tags: Optional[List[str]] = []


class PostResponse(BaseModel):
    id: UUID
    author_id: UUID
    title: str
    slug: str
    content: str
    summary: Optional[str]
    status: str
    view_count: int
    tags: List[TagResponse]
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]

    class Config:
        from_attributes = True


class PostListItem(BaseModel):
    id: UUID
    author_id: UUID
    title: str
    slug: str
    summary: Optional[str]
    status: str
    view_count: int
    tags: List[TagResponse]
    created_at: datetime
    published_at: Optional[datetime]
    author_username: Optional[str] = None

    class Config:
        from_attributes = True


class APIResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    message: str
    errors: Optional[list] = None


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)
