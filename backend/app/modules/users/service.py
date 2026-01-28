"""User service."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from datetime import datetime, timedelta, timezone
import secrets

from app.models import User
from app.auth.utils import hash_password
from .schemas import UserCreate, UserUpdate, UserInvite


class UserService:
    """Service for user operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def list_users(self, tenant_id: UUID | None = None) -> list[User]:
        """List users, optionally filtered by tenant."""
        query = select(User).options(selectinload(User.role))
        if tenant_id:
            query = query.where(User.tenant_id == tenant_id)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_user(self, user_id: UUID) -> User | None:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).options(selectinload(User.role)).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create_user(self, data: UserCreate) -> User:
        """Create a new user."""
        user = User(
            **data.model_dump(exclude={'password'}),
            password_hash=hash_password(data.password) if data.password else None
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        # Load role relationship
        await self.db.refresh(user, ['role'])
        return user
    
    async def update_user(self, user_id: UUID, data: UserUpdate) -> User:
        """Update user."""
        user = await self.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        update_data = data.model_dump(exclude_unset=True)
        if 'password' in update_data:
            update_data['password_hash'] = hash_password(update_data.pop('password'))
        
        for key, value in update_data.items():
            setattr(user, key, value)
        
        await self.db.commit()
        await self.db.refresh(user, ['role'])
        return user
    
    async def invite_user(self, data: UserInvite) -> User:
        """Invite a user by creating an account with invitation token."""
        token = secrets.token_urlsafe(32)
        user = User(
            email=data.email,
            full_name=data.full_name,
            tenant_id=data.tenant_id,
            role_id=data.role_id,
            invitation_token=token,
            invitation_expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        # TODO: отправить email с приглашением
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user, ['role'])
        return user
    
    async def deactivate_user(self, user_id: UUID) -> None:
        """Deactivate user."""
        user = await self.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        user.is_active = False
        await self.db.commit()
