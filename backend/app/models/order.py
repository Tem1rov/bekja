"""Order models: Order, OrderItem, Reservation."""

import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text, Integer, Numeric, DateTime, UniqueConstraint, func
from sqlalchemy import Computed
from decimal import Decimal
from uuid import UUID, uuid4
from datetime import datetime

from app.models.base import Base, TimestampMixin

# Forward references for type hints
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.tenant import Tenant
    from app.models.user import User
    from app.models.product import Product
    from app.models.warehouse import Inventory
    from app.models.integration import Integration


class OrderStatus(str, enum.Enum):
    """Order status enum."""
    NEW = "new"
    CONFIRMED = "confirmed"
    AWAITING_STOCK = "awaiting_stock"
    PICKING = "picking"
    PACKED = "packed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(Base, TimestampMixin):
    """Order."""
    
    __tablename__ = "orders"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    order_number: Mapped[str] = mapped_column(String(50), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False)  # manual, ozon, wildberries, yandex
    integration_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("integrations.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    status: Mapped[OrderStatus] = mapped_column(
        default=OrderStatus.NEW,
        nullable=False,
        index=True
    )
    
    # Customer data
    customer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    customer_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    customer_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    delivery_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    delivery_method: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # Amounts
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0"),
        server_default="0",
        nullable=False
    )
    
    # PnL fields
    cost_of_goods: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0"),
        server_default="0",
        nullable=False
    )
    marketplace_fee: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0"),
        server_default="0",
        nullable=False
    )
    shipping_cost: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0"),
        server_default="0",
        nullable=False
    )
    storage_cost: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0"),
        server_default="0",
        nullable=False
    )
    processing_cost: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0"),
        server_default="0",
        nullable=False
    )
    packaging_cost: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0"),
        server_default="0",
        nullable=False
    )
    other_costs: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0"),
        server_default="0",
        nullable=False
    )
    margin: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        Computed(
            "total_amount - cost_of_goods - marketplace_fee - shipping_cost - "
            "storage_cost - processing_cost - packaging_cost - other_costs",
            persisted=True
        ),
        nullable=False
    )
    has_manual_adjustments: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    # Dates
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    picked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    shipped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # Metadata
    assigned_picker: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'order_number', name='uq_order_tenant_number'),
        UniqueConstraint('tenant_id', 'status', 'created_at', name='idx_orders_tenant_status_created'),
    )
    
    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant")
    items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    picker: Mapped["User | None"] = relationship("User", foreign_keys=[assigned_picker])
    integration: Mapped["Integration | None"] = relationship("Integration")


class OrderItem(Base):
    """Order item."""
    
    __tablename__ = "order_items"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    order_id: Mapped[UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    product_id: Mapped[UUID] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    quantity: Mapped[int] = mapped_column(nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    cost_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    reserved_quantity: Mapped[int] = mapped_column(default=0, nullable=False)
    picked_quantity: Mapped[int] = mapped_column(default=0, nullable=False)
    shortage: Mapped[int] = mapped_column(default=0, nullable=False)  # Недостающее количество
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=func.now(),
        nullable=False
    )
    
    __table_args__ = (
        UniqueConstraint('order_id', 'product_id', name='uq_order_item_order_product'),
    )
    
    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product")
    reservations: Mapped[list["Reservation"]] = relationship("Reservation", back_populates="order_item")


class Reservation(Base):
    """Reservation (link between order item and inventory)."""
    
    __tablename__ = "reservations"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    order_id: Mapped[UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    order_item_id: Mapped[UUID] = mapped_column(
        ForeignKey("order_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    inventory_id: Mapped[UUID] = mapped_column(
        ForeignKey("inventory.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    product_id: Mapped[UUID] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    cell_id: Mapped[UUID] = mapped_column(
        ForeignKey("cells.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    quantity: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="reserved", server_default="reserved", nullable=False)
    fulfilled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    order: Mapped["Order"] = relationship("Order")
    order_item: Mapped["OrderItem"] = relationship("OrderItem", back_populates="reservations")
    inventory: Mapped["Inventory"] = relationship("Inventory")


class OrderHistory(Base):
    """Order status change history."""
    
    __tablename__ = "order_history"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    order_id: Mapped[UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    old_status: Mapped[OrderStatus | None] = mapped_column(nullable=True)
    new_status: Mapped[OrderStatus] = mapped_column(nullable=False)
    changed_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False
    )
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    order: Mapped["Order"] = relationship("Order")
    user: Mapped["User"] = relationship("User")
