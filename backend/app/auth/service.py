"""Authentication service."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models import User
from app.auth.utils import verify_password, create_access_token, create_refresh_token


class AuthService:
    """Service for authentication operations."""
    
    @staticmethod
    async def authenticate_user(
        email: str,
        password: str,
        db: AsyncSession
    ) -> User | None:
        """Authenticate a user by email and password."""
        result = await db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        if not user.password_hash:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        if not user.is_active:
            return None
        
        return user
    
    @staticmethod
    def create_tokens(user: User) -> dict:
        """Create access and refresh tokens for a user."""
        token_data = {
            "sub": str(user.id),
            "tenant_id": str(user.tenant_id) if user.tenant_id else None,
            "role": user.role.name
        }
        
        return {
            "access_token": create_access_token(token_data),
            "refresh_token": create_refresh_token(token_data),
            "token_type": "bearer"
        }
