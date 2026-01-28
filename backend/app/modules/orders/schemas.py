"""Order schemas."""

from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from enum import Enum


class OrderStatus(str, Enum):
    """Order status enum."""
    NEW = "new"
    CONFIRMED = "confirmed"
    AWAITING_STOCK = "awaiting_stock"
    PICKING = "picking"
    PACKED = "packed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderItemCreate(BaseModel):
    """Order item create schema."""
    product_id: UUID
    quantity: int
    price: Decimal
    cost_price: Decimal | None = None


class OrderItemResponse(BaseModel):
    """Order item response schema."""
    id: UUID
    order_id: UUID
    product_id: UUID
    quantity: int
    price: Decimal
    cost_price: Decimal
    reserved_quantity: int
    picked_quantity: int
    shortage: int = 0

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """Order response schema."""
    id: UUID
    tenant_id: UUID
    order_number: str
    external_id: str | None = None
    source: str
    status: OrderStatus
    customer_name: str | None = None
    customer_phone: str | None = None
    customer_email: str | None = None
    delivery_address: str | None = None
    delivery_method: str | None = None
    total_amount: Decimal
    cost_of_goods: Decimal
    marketplace_fee: Decimal
    shipping_cost: Decimal
    storage_cost: Decimal
    processing_cost: Decimal
    packaging_cost: Decimal
    other_costs: Decimal
    margin: Decimal
    confirmed_at: datetime | None = None
    picked_at: datetime | None = None
    shipped_at: datetime | None = None
    delivered_at: datetime | None = None
    cancelled_at: datetime | None = None
    cancellation_reason: str | None = None
    assigned_picker: UUID | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse] = []

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    """Order create schema."""
    tenant_id: UUID
    order_number: str | None = None  # Автогенерация, если не указан
    external_id: str | None = None
    source: str = "manual"
    customer_name: str | None = None
    customer_phone: str | None = None
    customer_email: str | None = None
    delivery_address: str | None = None
    delivery_method: str | None = None
    items: list[OrderItemCreate]
    notes: str | None = None


class OrderUpdate(BaseModel):
    """Order update schema."""
    status: OrderStatus | None = None
    customer_name: str | None = None
    customer_phone: str | None = None
    customer_email: str | None = None
    delivery_address: str | None = None
    delivery_method: str | None = None
    assigned_picker: UUID | None = None
    notes: str | None = None
