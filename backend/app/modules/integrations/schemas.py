"""Integration schemas."""

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class IntegrationResponse(BaseModel):
    """Integration response schema."""
    id: UUID
    tenant_id: UUID
    marketplace: str
    name: str
    settings: dict
    sync_interval: int
    is_active: bool
    last_sync_at: datetime | None = None
    last_sync_status: str | None = None
    last_sync_error: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IntegrationCreate(BaseModel):
    """Integration create schema."""
    tenant_id: UUID
    marketplace: str
    name: str
    api_key: str
    api_secret: str | None = None
    settings: dict = {}
    sync_interval: int = 15
    is_active: bool = True


class IntegrationUpdate(BaseModel):
    """Integration update schema."""
    name: str | None = None
    api_key: str | None = None
    api_secret: str | None = None
    settings: dict | None = None
    sync_interval: int | None = None
    is_active: bool | None = None


class SyncResponse(BaseModel):
    """Sync response schema."""
    sync_id: UUID
    integration_id: UUID
    status: str
    started_at: datetime
    items_processed: int = 0
    items_created: int = 0
    items_updated: int = 0
    items_failed: int = 0
