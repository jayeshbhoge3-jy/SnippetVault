from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from .user import UserPublic

class SnippetBase(BaseModel):
    title: str = Field(..., max_length=255)
    code: str = Field(..., max_length=50000)
    language: str = Field(..., max_length=50)
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list, max_length=10)
    is_public: bool = False

class SnippetCreate(SnippetBase):
    pass

class SnippetUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    code: Optional[str] = Field(None, max_length=50000)
    language: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    tags: Optional[List[str]] = Field(None, max_length=10)
    is_public: Optional[bool] = None

class SnippetResponse(SnippetBase):
    id: UUID
    user_id: UUID
    share_id: str
    view_count: int
    star_count: int
    created_at: datetime
    updated_at: datetime
    is_starred: Optional[bool] = None # For authenticated requests

    model_config = ConfigDict(from_attributes=True)

class SnippetPublicResponse(SnippetResponse):
    author: UserPublic

class PaginatedSnippetResponse(BaseModel):
    items: List[SnippetResponse]
    total: int
    page: int
    size: int
