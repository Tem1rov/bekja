"""Tenant model."""

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, Numeric
from decimal import Decimal
from uuid import UUID, uuid4

from app.models.base import Base, TimestampMixin


class Tenant(Base, TimestampMixin):
    """Tenant (client-owner of products)."""
    
    __tablename__ = "tenants"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    inn: Mapped[str] = mapped_column(String(12), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    legal_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    storage_rate: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), 
        default=Decimal("0"),
        server_default="0",
        nullable=False
    )
    processing_rate: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0"),
        server_default="0",
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
