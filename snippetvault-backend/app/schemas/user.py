from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None

class UserCreate(UserBase):
    github_id: str

class UserResponse(UserBase):
    id: UUID
    plan: str
    snippets_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserPublic(BaseModel):
    username: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class UserStats(BaseModel):
    total_snippets: int
    public_snippets: int
    private_snippets: int
    total_stars_received: int
    total_views: int
    top_languages: List[str]
    most_used_tags: List[str]
    snippets_this_month: int
