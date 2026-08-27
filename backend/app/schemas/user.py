from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)
    display_name: str = Field(..., min_length=2, max_length=100)
    role: Optional[str] = "student"


class UserLogin(UserBase):
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    role: str
    display_name: str
    current_level: int
    total_xp: int
    rank_title: str
    streak_count: int


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class UserProfileUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=2, max_length=100)
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    target_unt_score: Optional[int] = Field(None, ge=1, le=50)


class UserProfileResponse(BaseModel):
    id: int
    user_id: int
    display_name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    target_unt_score: int
    current_level: int
    total_xp: int
    rank_title: str
    streak_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    is_verified: bool
    email_verified: bool = False
    last_login_at: Optional[datetime] = None
    created_at: datetime
    profile: Optional[UserProfileResponse] = None

    model_config = ConfigDict(from_attributes=True)
