"""Dashboard router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.auth.permissions import require_permission, Permission, get_tenant_filter
from app.database import get_db
from app.models import User
from .schemas import DashboardDataResponse
from .service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardDataResponse)
async def get_dashboard_data(
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID | None = Depends(get_tenant_filter),
    user: User = Depends(require_permission(Permission.ORDERS_VIEW))
):
    """Get dashboard data for current tenant."""
    # Использовать tenant_id из пользователя, если не указан явно
    effective_tenant_id = tenant_id if tenant_id else user.tenant_id
    
    service = DashboardService(db)
    data = await service.get_dashboard_data(effective_tenant_id)
    
    return DashboardDataResponse(**data)
