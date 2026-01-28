"""Tenant schemas."""

from pydantic import BaseModel, EmailStr
from uuid import UUID
from decimal import Decimal
from datetime import datetime


class TenantResponse(BaseModel):
    """Tenant response schema."""
    id: UUID
    name: str
    inn: str
    email: EmailStr
    phone: str | None = None
    legal_address: str | None = None
    storage_rate: Decimal
    processing_rate: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TenantCreate(BaseModel):
    """Tenant create schema."""
    name: str
    inn: str
    email: EmailStr
    phone: str | None = None
    legal_address: str | None = None
    storage_rate: Decimal = Decimal("0")
    processing_rate: Decimal = Decimal("0")
    is_active: bool = True


class TenantUpdate(BaseModel):
    """Tenant update schema."""
    name: str | None = None
    inn: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    legal_address: str | None = None
    storage_rate: Decimal | None = None
    processing_rate: Decimal | None = None
    is_active: bool | None = None
