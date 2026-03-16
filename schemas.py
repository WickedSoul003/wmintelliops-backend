from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class RegisterRequest(BaseModel):
    organization_id: str  = Field(..., min_length=3, max_length=50)
    organization_name: str = Field(..., min_length=2, max_length=100)
    full_name:  str        = Field(..., min_length=2, max_length=100)
    email:      EmailStr
    password:   str        = Field(..., min_length=6)
    role:       Optional[str] = "admin"


class LoginRequest(BaseModel):
    organization_id: str
    email:           EmailStr
    password:        str


class UserResponse(BaseModel):
    id:               str
    organization_id:  str
    organization_name: str
    full_name:        str
    email:            str
    role:             str
    created_at:       datetime


class TokenResponse(BaseModel):
    access_token:  str
    token_type:    str = "bearer"
    user:          UserResponse


class MessageResponse(BaseModel):
    message: str
    success: bool = True
