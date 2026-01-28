"""Notification models."""

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import func
from uuid import UUID, uuid4
from datetime import datetime
from typing import Dict, Any

from app.models.base import Base, TimestampMixin

# Forward references for type hints
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User


class Notification(Base, TimestampMixin):
    """User notification."""
    
    __tablename__ = "notifications"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    data: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        server_default="{}",
        nullable=False
    )
    is_read: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
