"""Base classes for SQLAlchemy models."""

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import func
from datetime import datetime


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        onupdate=func.now(),
        server_default=func.now(),
        nullable=False
    )
