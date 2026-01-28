"""Finance schemas."""

from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
from datetime import datetime, date


class TariffResponse(BaseModel):
    """Tariff response schema."""
    id: UUID
    tenant_id: UUID
    processing_rate: Decimal
    storage_rate: Decimal
    packaging_rate: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TariffUpdate(BaseModel):
    """Tariff update schema."""
    processing_rate: Decimal | None = None
    storage_rate: Decimal | None = None
    packaging_rate: Decimal | None = None


class PnLResponse(BaseModel):
    """PnL response schema."""
    order_id: str
    revenue: float
    cost_of_goods: float
    processing_cost: float
    storage_cost: float
    marketplace_fee: float
    total_expenses: float
    margin: float
    margin_percent: float


class PnLReportResponse(BaseModel):
    """PnL report response schema."""
    period: dict
    total_revenue: float
    total_expenses: float
    total_margin: float
    margin_percent: float
    orders_count: int
    orders: list[dict] = []
