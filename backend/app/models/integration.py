"""Integration models: Integration, SyncLog."""

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text, Integer, Boolean, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from uuid import UUID, uuid4
from datetime import datetime
from typing import Dict, Any

from sqlalchemy import func
from app.models.base import Base, TimestampMixin

# Forward references for type hints
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.tenant import Tenant


class Integration(Base, TimestampMixin):
    """Marketplace integration."""
    
    __tablename__ = "integrations"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    marketplace: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    api_key_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    api_secret_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    settings: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        server_default="{}",
        nullable=False
    )
    sync_interval: Mapped[int] = mapped_column(default=15, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_sync_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    last_sync_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant")
    sync_logs: Mapped[list["SyncLog"]] = relationship("SyncLog", back_populates="integration")


class SyncLog(Base):
    """Sync log."""
    
    __tablename__ = "sync_logs"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    integration_id: Mapped[UUID] = mapped_column(
        ForeignKey("integrations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    sync_type: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    items_processed: Mapped[int] = mapped_column(default=0, nullable=False)
    items_created: Mapped[int] = mapped_column(default=0, nullable=False)
    items_updated: Mapped[int] = mapped_column(default=0, nullable=False)
    items_failed: Mapped[int] = mapped_column(default=0, nullable=False)
    error_details: Mapped[Dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=func.now(),
        nullable=False,
        index=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    integration: Mapped["Integration"] = relationship("Integration", back_populates="sync_logs")
