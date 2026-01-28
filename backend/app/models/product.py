"""Product and Category models."""

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text, Numeric, Boolean, UniqueConstraint, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from decimal import Decimal
from uuid import UUID, uuid4
from datetime import datetime

from app.models.base import Base, TimestampMixin


class Category(Base, TimestampMixin):
    """Product category."""
    
    __tablename__ = "categories"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True
    )
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'name', 'parent_id', name='uq_category_tenant_name_parent'),
    )
    
    # Relationships
    parent: Mapped["Category | None"] = relationship("Category", remote_side=[id])
    products: Mapped[list["Product"]] = relationship("Product", back_populates="category")


class Product(Base, TimestampMixin):
    """Product (SKU)."""
    
    __tablename__ = "products"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    sku: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    barcode: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    unit: Mapped[str] = mapped_column(String(20), default="шт", server_default="шт", nullable=False)
    weight: Mapped[Decimal | None] = mapped_column(Numeric(10, 3), nullable=True)
    length: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    width: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    height: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    cost_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0"),
        server_default="0",
        nullable=False
    )
    min_stock_level: Mapped[int] = mapped_column(default=0, nullable=False)
    expiry_tracking: Mapped[bool] = mapped_column(default=False, nullable=False)
    storage_requirements: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        server_default="{}",
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'sku', name='uq_product_tenant_sku'),
    )
    
    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant")
    category: Mapped["Category | None"] = relationship("Category", back_populates="products")
    cost_history: Mapped[list["ProductCostHistory"]] = relationship("ProductCostHistory", back_populates="product")


class ProductCostHistory(Base):
    """Product cost price change history."""
    
    __tablename__ = "product_cost_history"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    product_id: Mapped[UUID] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    old_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    new_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="cost_history")
