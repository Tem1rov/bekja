"""Tenants router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.auth.permissions import require_permission, Permission
from app.database import get_db
from .schemas import TenantResponse, TenantCreate, TenantUpdate
from .service import TenantService

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get("", response_model=list[TenantResponse])
async def list_tenants(
    user=Depends(require_permission(Permission.TENANTS_VIEW)),
    db: AsyncSession = Depends(get_db)
):
    """List tenants."""
    service = TenantService(db)
    tenants = await service.list_tenants()
    return [TenantResponse.model_validate(tenant) for tenant in tenants]


@router.post("", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    data: TenantCreate,
    user=Depends(require_permission(Permission.TENANTS_CREATE)),
    db: AsyncSession = Depends(get_db)
):
    """Create tenant."""
    service = TenantService(db)
    tenant = await service.create_tenant(data)
    return TenantResponse.model_validate(tenant)


@router.get("/{id}", response_model=TenantResponse)
async def get_tenant(
    id: UUID,
    user=Depends(require_permission(Permission.TENANTS_VIEW)),
    db: AsyncSession = Depends(get_db)
):
    """Get tenant by ID."""
    service = TenantService(db)
    tenant = await service.get_tenant(id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    return TenantResponse.model_validate(tenant)


@router.put("/{id}", response_model=TenantResponse)
async def update_tenant(
    id: UUID,
    data: TenantUpdate,
    user=Depends(require_permission(Permission.TENANTS_EDIT)),
    db: AsyncSession = Depends(get_db)
):
    """Update tenant."""
    service = TenantService(db)
    try:
        tenant = await service.update_tenant(id, data)
        return TenantResponse.model_validate(tenant)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_tenant(
    id: UUID,
    user=Depends(require_permission(Permission.TENANTS_EDIT)),
    db: AsyncSession = Depends(get_db)
):
    """Deactivate tenant."""
    service = TenantService(db)
    try:
        await service.deactivate_tenant(id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
