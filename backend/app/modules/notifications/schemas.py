"""Notification schemas."""

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Dict, Any


class NotificationResponse(BaseModel):
    """Notification response schema."""
    id: UUID
    user_id: UUID
    type: str
    title: str
    message: str
    data: Dict[str, Any]
    is_read: bool
    read_at: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationCreate(BaseModel):
    """Notification create schema."""
    type: str
    title: str
    message: str
    data: Dict[str, Any] | None = None


class NotificationListResponse(BaseModel):
    """Notification list response schema."""
    items: list[NotificationResponse]
    total: int
    unread_count: int
