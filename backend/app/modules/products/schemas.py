"""Product schemas."""

from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
from datetime import datetime


class ProductResponse(BaseModel):
    """Product response schema."""
    id: UUID
    tenant_id: UUID
    sku: str
    name: str
    category_id: UUID | None = None
    barcode: str | None = None
    unit: str
    weight: Decimal | None = None
    length: Decimal | None = None
    width: Decimal | None = None
    height: Decimal | None = None
    cost_price: Decimal
    min_stock_level: int
    expiry_tracking: bool
    storage_requirements: dict
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    """Product create schema."""
    sku: str
    name: str
    category_id: UUID | None = None
    barcode: str | None = None
    unit: str = "шт"
    weight: Decimal | None = None
    length: Decimal | None = None
    width: Decimal | None = None
    height: Decimal | None = None
    cost_price: Decimal = Decimal("0")
    min_stock_level: int = 0
    expiry_tracking: bool = False
    storage_requirements: dict = {}
    is_active: bool = True


class ProductUpdate(BaseModel):
    """Product update schema."""
    sku: str | None = None
    name: str | None = None
    category_id: UUID | None = None
    barcode: str | None = None
    unit: str | None = None
    weight: Decimal | None = None
    length: Decimal | None = None
    width: Decimal | None = None
    height: Decimal | None = None
    cost_price: Decimal | None = None
    min_stock_level: int | None = None
    expiry_tracking: bool | None = None
    storage_requirements: dict | None = None
    is_active: bool | None = None


class ProductImportResponse(BaseModel):
    """Product import response schema."""
    imported: int
    updated: int
    failed: int
    errors: list[str] = []
