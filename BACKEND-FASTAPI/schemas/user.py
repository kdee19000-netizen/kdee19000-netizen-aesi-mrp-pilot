"""Pydantic schemas for user management."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=64)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    role: str = "viewer"
    preferred_language: str = "en"


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    preferred_language: str

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
