"""Dashboard schemas."""

from pydantic import BaseModel
from typing import Optional


class DashboardDataResponse(BaseModel):
    """Dashboard data response schema."""
    orders_today: int
    orders_by_status: dict[str, int]
    pnl_today: dict
    low_stock_count: int
    low_stock_items: list[dict]
    
    class Config:
        from_attributes = True
