"""Authentication schemas."""

from pydantic import BaseModel, EmailStr
from uuid import UUID


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Token payload schema."""
    sub: str  # user_id
    tenant_id: str | None
    role: str
    exp: int


class UserResponse(BaseModel):
    """User response schema."""
    id: UUID
    email: str
    full_name: str
    role: str
    tenant_id: UUID | None

    class Config:
        from_attributes = True


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str
