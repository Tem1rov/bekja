"""Finance models: Tariff, StorageCharge, OrderAdjustment."""

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text, Integer, Numeric, Date, DateTime, UniqueConstraint
from decimal import Decimal
from uuid import UUID, uuid4
from datetime import date, datetime

from sqlalchemy import func
from app.models.base import Base, TimestampMixin

# Forward references for type hints
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.tenant import Tenant
    from app.models.product import Product
    from app.models.order import Order
    from app.models.user import User
    from app.models.integration import Integration


class Tariff(Base, TimestampMixin):
    """Tariff (pricing configuration per tenant)."""
    
    __tablename__ = "tariffs"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    processing_rate: Mapped[Decimal] = mapped_column(
        Numeric(10, 4),
        default=Decimal("0"),
        server_default="0",
        nullable=False
    )
    storage_rate: Mapped[Decimal] = mapped_column(
        Numeric(10, 4),
        default=Decimal("0"),
        server_default="0",
        nullable=False
    )
    packaging_rate: Mapped[Decimal] = mapped_column(
        Numeric(10, 4),
        default=Decimal("0"),
        server_default="0",
        nullable=False
    )
    
    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant")


class StorageCharge(Base):
    """Storage charge (daily calculation)."""
    
    __tablename__ = "storage_charges"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    order_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    charge_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    product_id: Mapped[UUID] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False
    )
    quantity: Mapped[int] = mapped_column(nullable=False)
    rate: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=func.now(),
        nullable=False
    )
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'charge_date', 'product_id', name='uq_storage_charge_tenant_date_product'),
    )
    
    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant")
    product: Mapped["Product"] = relationship("Product")
    order: Mapped["Order | None"] = relationship("Order")


class OrderAdjustment(Base):
    """Manual PnL adjustment."""
    
    __tablename__ = "order_adjustments"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    order_id: Mapped[UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    adjustment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    order: Mapped["Order"] = relationship("Order")
    creator: Mapped["User"] = relationship("User")


class MarketplaceFee(Base, TimestampMixin):
    """Marketplace fee configuration."""
    
    __tablename__ = "marketplace_fees"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    integration_id: Mapped[UUID] = mapped_column(
        ForeignKey("integrations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    fee_type: Mapped[str] = mapped_column(String(20), nullable=False)  # "percent" or "fixed"
    fee_value: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    
    # Relationships
    integration: Mapped["Integration"] = relationship("Integration")
