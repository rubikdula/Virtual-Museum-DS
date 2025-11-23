from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Comment Schemas
class CommentBase(BaseModel):
    text: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    artifact_id: int
    user_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Artifact Schemas
class ArtifactBase(BaseModel):
    title: str
    short_description: str
    long_description: Optional[str] = None
    year: Optional[str] = None
    era: Optional[str] = "Modern"
    category: str
    tags: Optional[str] = None
    media_type: str
    media_url: str

class ArtifactCreate(ArtifactBase):
    pass

class Artifact(ArtifactBase):
    id: int
    creator_id: int
    views_count: int
    likes_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    creator: User

    class Config:
        from_attributes = True
