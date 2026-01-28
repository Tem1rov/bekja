"""Users router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.auth.permissions import require_permission, Permission
from app.auth.dependencies import get_current_user
from app.database import get_db
from .schemas import UserResponse, UserCreate, UserUpdate, UserInvite
from .service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
async def list_users(
    user=Depends(require_permission(Permission.USERS_VIEW)),
    db: AsyncSession = Depends(get_db)
):
    """List users. Filtered by tenant for non-admin users."""
    service = UserService(db)
    # Tenant isolation: non-admin users see only their tenant's users
    tenant_id = None if user.role.name == "admin" else user.tenant_id
    users = await service.list_users(tenant_id=tenant_id)
    return [UserResponse.model_validate(u) for u in users]


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    user=Depends(require_permission(Permission.USERS_CREATE)),
    db: AsyncSession = Depends(get_db)
):
    """Create user."""
    service = UserService(db)
    # Tenant isolation: non-admin users can only create users for their tenant
    if user.role.name != "admin" and data.tenant_id != user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create user for different tenant"
        )
    created_user = await service.create_user(data)
    return UserResponse.model_validate(created_user)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user=Depends(get_current_user)
):
    """Get current user info."""
    return UserResponse.model_validate(current_user)


@router.put("/{id}", response_model=UserResponse)
async def update_user(
    id: UUID,
    data: UserUpdate,
    user=Depends(require_permission(Permission.USERS_EDIT)),
    db: AsyncSession = Depends(get_db)
):
    """Update user."""
    service = UserService(db)
    # Tenant isolation: check if user belongs to same tenant
    target_user = await service.get_user(id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.role.name != "admin" and target_user.tenant_id != user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update user from different tenant"
        )
    
    try:
        updated_user = await service.update_user(id, data)
        return UserResponse.model_validate(updated_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    id: UUID,
    user=Depends(require_permission(Permission.USERS_EDIT)),
    db: AsyncSession = Depends(get_db)
):
    """Deactivate user."""
    service = UserService(db)
    # Tenant isolation: check if user belongs to same tenant
    target_user = await service.get_user(id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.role.name != "admin" and target_user.tenant_id != user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot deactivate user from different tenant"
        )
    
    try:
        await service.deactivate_user(id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/invite", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def invite_user(
    data: UserInvite,
    user=Depends(require_permission(Permission.USERS_CREATE)),
    db: AsyncSession = Depends(get_db)
):
    """Invite user."""
    service = UserService(db)
    # Tenant isolation: non-admin users can only invite users for their tenant
    if user.role.name != "admin" and data.tenant_id != user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot invite user for different tenant"
        )
    invited_user = await service.invite_user(data)
    return UserResponse.model_validate(invited_user)
