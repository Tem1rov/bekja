"""User schemas."""

from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime


class RoleResponse(BaseModel):
    """Role response schema."""
    id: int
    name: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """User response schema."""
    id: UUID
    tenant_id: UUID | None = None
    role_id: int
    email: EmailStr
    full_name: str
    phone: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    role: RoleResponse | None = None

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """User create schema."""
    tenant_id: UUID | None = None
    role_id: int
    email: EmailStr
    password: str
    full_name: str
    phone: str | None = None
    is_active: bool = True


class UserUpdate(BaseModel):
    """User update schema."""
    tenant_id: UUID | None = None
    role_id: int | None = None
    email: EmailStr | None = None
    password: str | None = None
    full_name: str | None = None
    phone: str | None = None
    is_active: bool | None = None


class UserInvite(BaseModel):
    """User invite schema."""
    email: EmailStr
    full_name: str
    tenant_id: UUID
    role_id: int
