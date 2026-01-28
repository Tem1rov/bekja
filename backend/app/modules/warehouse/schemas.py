"""Warehouse schemas."""

from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
from datetime import datetime, date


class WarehouseResponse(BaseModel):
    """Warehouse response schema."""
    id: UUID
    name: str
    address: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ZoneResponse(BaseModel):
    """Zone response schema."""
    id: UUID
    warehouse_id: UUID
    name: str
    zone_type: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ZoneCreate(BaseModel):
    """Zone create schema."""
    name: str
    zone_type: str | None = None
    is_active: bool = True


class RackCreate(BaseModel):
    """Rack create schema."""
    code: str
    levels: int = 1
    is_active: bool = True


class RackResponse(BaseModel):
    """Rack response schema."""
    id: UUID
    zone_id: UUID
    code: str
    levels: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CellResponse(BaseModel):
    """Cell response schema."""
    id: UUID
    rack_id: UUID
    code: str
    level: int
    size: str
    max_weight: Decimal | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InventoryResponse(BaseModel):
    """Inventory response schema."""
    id: UUID
    cell_id: UUID
    product_id: UUID
    tenant_id: UUID
    quantity: int
    reserved_quantity: int
    lot_number: str | None = None
    expiry_date: date | None = None
    received_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReceiptCreate(BaseModel):
    """Receipt create schema."""
    warehouse_id: UUID
    tenant_id: UUID
    items: list[dict]  # Simplified for stub


class TransferCreate(BaseModel):
    """Transfer create schema."""
    from_cell_id: UUID
    to_cell_id: UUID
    product_id: UUID
    quantity: int
    lot_number: str | None = None
