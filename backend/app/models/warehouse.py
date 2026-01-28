"""Warehouse models: Warehouse, Zone, Rack, Cell, Inventory."""

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text, Integer, Numeric, Boolean, Date, DateTime, UniqueConstraint
from decimal import Decimal
from uuid import UUID, uuid4
from datetime import datetime, date

from app.models.base import Base, TimestampMixin


class Warehouse(Base, TimestampMixin):
    """Warehouse."""
    
    __tablename__ = "warehouses"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    
    # Relationships
    zones: Mapped[list["Zone"]] = relationship("Zone", back_populates="warehouse")


class Zone(Base, TimestampMixin):
    """Warehouse zone."""
    
    __tablename__ = "warehouse_zones"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    warehouse_id: Mapped[UUID] = mapped_column(
        ForeignKey("warehouses.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    zone_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('warehouse_id', 'name', name='uq_zone_warehouse_name'),
    )
    
    # Relationships
    warehouse: Mapped["Warehouse"] = relationship("Warehouse", back_populates="zones")
    racks: Mapped[list["Rack"]] = relationship("Rack", back_populates="zone")


class Rack(Base, TimestampMixin):
    """Rack in a zone."""
    
    __tablename__ = "racks"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    zone_id: Mapped[UUID] = mapped_column(
        ForeignKey("warehouse_zones.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    levels: Mapped[int] = mapped_column(default=1, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('zone_id', 'code', name='uq_rack_zone_code'),
    )
    
    # Relationships
    zone: Mapped["Zone"] = relationship("Zone", back_populates="racks")
    cells: Mapped[list["Cell"]] = relationship("Cell", back_populates="rack")


class Cell(Base, TimestampMixin):
    """Cell in a rack."""
    
    __tablename__ = "cells"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    rack_id: Mapped[UUID] = mapped_column(
        ForeignKey("racks.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    level: Mapped[int] = mapped_column(default=1, nullable=False)
    size: Mapped[str] = mapped_column(String(10), default="M", server_default="M", nullable=False)
    max_weight: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('rack_id', 'code', name='uq_cell_rack_code'),
    )
    
    # Relationships
    rack: Mapped["Rack"] = relationship("Rack", back_populates="cells")
    inventory: Mapped[list["Inventory"]] = relationship("Inventory", back_populates="cell")


class Inventory(Base, TimestampMixin):
    """Inventory in a cell."""
    
    __tablename__ = "inventory"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    cell_id: Mapped[UUID] = mapped_column(
        ForeignKey("cells.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    product_id: Mapped[UUID] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    quantity: Mapped[int] = mapped_column(default=0, nullable=False)
    reserved_quantity: Mapped[int] = mapped_column(default=0, nullable=False)
    lot_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'product_id', 'cell_id', name='uq_inventory_tenant_product_cell'),
    )
    
    # Relationships
    cell: Mapped["Cell"] = relationship("Cell", back_populates="inventory")
    product: Mapped["Product"] = relationship("Product")
    tenant: Mapped["Tenant"] = relationship("Tenant")


class Receipt(Base, TimestampMixin):
    """Receipt document."""
    
    __tablename__ = "receipts"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    receipt_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(30), default="draft", nullable=False, index=True)
    expected_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    supplier: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    items: Mapped[list["ReceiptItem"]] = relationship("ReceiptItem", back_populates="receipt", cascade="all, delete-orphan")
    tenant: Mapped["Tenant"] = relationship("Tenant")


class ReceiptItem(Base, TimestampMixin):
    """Receipt item."""
    
    __tablename__ = "receipt_items"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    receipt_id: Mapped[UUID] = mapped_column(
        ForeignKey("receipts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    product_id: Mapped[UUID] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False
    )
    expected_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    received_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cell_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("cells.id", ondelete="SET NULL"),
        nullable=True
    )
    lot_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Relationships
    receipt: Mapped["Receipt"] = relationship("Receipt", back_populates="items")
    product: Mapped["Product"] = relationship("Product")
    cell: Mapped["Cell | None"] = relationship("Cell")


class Transfer(Base, TimestampMixin):
    """Transfer between cells."""
    
    __tablename__ = "transfers"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    product_id: Mapped[UUID] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False
    )
    source_cell_id: Mapped[UUID] = mapped_column(
        ForeignKey("cells.id", ondelete="CASCADE"),
        nullable=False
    )
    target_cell_id: Mapped[UUID] = mapped_column(
        ForeignKey("cells.id", ondelete="CASCADE"),
        nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    lot_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False
    )
    
    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant")
    product: Mapped["Product"] = relationship("Product")
    source_cell: Mapped["Cell"] = relationship("Cell", foreign_keys=[source_cell_id])
    target_cell: Mapped["Cell"] = relationship("Cell", foreign_keys=[target_cell_id])
