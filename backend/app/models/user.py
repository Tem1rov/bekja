"""User, Role, and Session models."""

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Integer, JSON, DateTime, Text, Index, func
from sqlalchemy.dialects.postgresql import JSONB, INET
from datetime import datetime
from uuid import UUID, uuid4
from typing import Dict, Any

from app.models.base import Base, TimestampMixin

# Forward reference for type hints
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.tenant import Tenant


class Role(Base):
    """User role with permissions."""
    
    __tablename__ = "roles"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    permissions: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        server_default="{}",
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    users: Mapped[list["User"]] = relationship("User", back_populates="role")


class User(Base, TimestampMixin):
    """User account."""
    
    __tablename__ = "users"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id"),
        nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    
    # Invitation fields
    invitation_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    invitation_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Password reset fields
    password_reset_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_reset_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Security fields
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    failed_login_attempts: Mapped[int] = mapped_column(default=0, nullable=False)
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Relationships
    role: Mapped["Role"] = relationship("Role", back_populates="users")
    tenant: Mapped["Tenant | None"] = relationship("Tenant", foreign_keys=[tenant_id])


class Session(Base):
    """User session for refresh tokens."""
    
    __tablename__ = "sessions"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    refresh_token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User")
