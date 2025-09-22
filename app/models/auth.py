"""Authentication models for request/response schemas"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserSignup(BaseModel):
    """User signup request model"""
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    display_name: Optional[str] = Field(None, max_length=100)
    preferred_language: Optional[str] = Field(default="en", description="Preferred language code")

class UserLogin(BaseModel):
    """User login request model"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """User response model"""
    uid: str
    email: str
    display_name: Optional[str] = None
    created_at: Optional[datetime] = None
    preferred_language: Optional[str] = "en"

class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class PasswordReset(BaseModel):
    """Password reset request model"""
    email: EmailStr

class PasswordUpdate(BaseModel):
    """Password update request model"""
    current_password: str
    new_password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    """User profile update model"""
    display_name: Optional[str] = None
    preferred_language: Optional[str] = None