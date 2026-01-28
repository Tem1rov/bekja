"""Permission system for RBAC."""

from enum import Enum
from typing import Optional
from uuid import UUID
from fastapi import HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.models import User
from app.database import get_db


class Permission(str, Enum):
    """Permission enum for role-based access control."""
    
    # Tenants
    TENANTS_VIEW = "tenants:view"
    TENANTS_CREATE = "tenants:create"
    TENANTS_EDIT = "tenants:edit"
    
    # Users
    USERS_VIEW = "users:view"
    USERS_CREATE = "users:create"
    USERS_EDIT = "users:edit"
    
    # Products
    PRODUCTS_VIEW = "products:view"
    PRODUCTS_CREATE = "products:create"
    PRODUCTS_EDIT = "products:edit"
    
    # Orders
    ORDERS_VIEW = "orders:view"
    ORDERS_CREATE = "orders:create"
    ORDERS_EDIT = "orders:edit"
    
    # Warehouse
    WAREHOUSE_VIEW = "warehouse:view"
    WAREHOUSE_MANAGE = "warehouse:manage"
    WAREHOUSE_INVENTORY = "warehouse:inventory"
    
    # Finance
    FINANCE_VIEW = "finance:view"
    FINANCE_EDIT = "finance:edit"
    FINANCE_REPORTS = "finance:reports"


ROLE_PERMISSIONS = {
    "admin": [p for p in Permission],  # All permissions
    "manager": [
        Permission.TENANTS_VIEW,
        Permission.USERS_VIEW,
        Permission.USERS_CREATE,
        Permission.PRODUCTS_VIEW,
        Permission.PRODUCTS_CREATE,
        Permission.PRODUCTS_EDIT,
        Permission.ORDERS_VIEW,
        Permission.ORDERS_CREATE,
        Permission.ORDERS_EDIT,
        Permission.WAREHOUSE_VIEW,
        Permission.WAREHOUSE_INVENTORY,
        Permission.FINANCE_VIEW,
        Permission.FINANCE_REPORTS,
    ],
    "warehouse": [
        Permission.PRODUCTS_VIEW,
        Permission.ORDERS_VIEW,
        Permission.WAREHOUSE_VIEW,
        Permission.WAREHOUSE_MANAGE,
        Permission.WAREHOUSE_INVENTORY,
    ],
    "client": [
        Permission.PRODUCTS_VIEW,
        Permission.ORDERS_VIEW,
        Permission.ORDERS_CREATE,
        Permission.FINANCE_VIEW,
        Permission.FINANCE_REPORTS,
    ],
}


def require_permission(*permissions: Permission):
    """Dependency to check permissions."""
    async def checker(user: User = Depends(get_current_user)):
        role_name = user.role.name if user.role else None
        if role_name not in ROLE_PERMISSIONS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Unknown role"
            )
        
        user_perms = ROLE_PERMISSIONS[role_name]
        for perm in permissions:
            if perm not in user_perms:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission required: {perm.value}"
                )
        return user
    return checker


def require_role(*roles: str):
    """Dependency to check role."""
    async def checker(user: User = Depends(get_current_user)):
        role_name = user.role.name if user.role else None
        if role_name not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Role not allowed"
            )
        return user
    return checker


def get_tenant_filter(user: User = Depends(get_current_user)) -> Optional[UUID]:
    """Returns tenant_id for filtering queries. Admin sees all."""
    if user.role.name == "admin":
        return None  # No filter for admin
    return user.tenant_id


async def get_db_with_tenant(
    db: AsyncSession = Depends(get_db),
    tenant_id: Optional[UUID] = Depends(get_tenant_filter)
):
    """Returns db session with tenant context."""
    return db, tenant_id
