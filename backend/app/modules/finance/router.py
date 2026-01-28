"""Finance router."""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from uuid import UUID
from datetime import date

from app.auth.permissions import require_permission, Permission, get_tenant_filter
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import TariffResponse, TariffUpdate, PnLResponse, PnLReportResponse
from .service import TariffService, PnLService

router = APIRouter(prefix="/finance", tags=["finance"])


@router.get("/tariffs", response_model=TariffResponse | None)
async def get_tariffs(
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID | None = Depends(get_tenant_filter),
    user: User = Depends(require_permission(Permission.FINANCE_VIEW))
):
    """Get tariffs for current tenant."""
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant ID is required"
        )
    
    service = TariffService(db)
    tariff = await service.get_tariffs(tenant_id)
    return tariff


@router.put("/tariffs", response_model=TariffResponse)
async def update_tariffs(
    data: TariffUpdate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID | None = Depends(get_tenant_filter),
    user: User = Depends(require_permission(Permission.FINANCE_EDIT))
):
    """Create or update tariffs for current tenant."""
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant ID is required"
        )
    
    service = TariffService(db)
    tariff = await service.update_tariffs(tenant_id, data)
    return tariff


@router.get("/orders/{order_id}/pnl", response_model=PnLResponse)
async def get_order_pnl(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID | None = Depends(get_tenant_filter),
    user: User = Depends(require_permission(Permission.FINANCE_VIEW))
):
    """Get PnL for an order."""
    service = PnLService(db)
    try:
        pnl = await service.calculate_order_pnl(order_id)
        return PnLResponse(**pnl)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/reports/pnl", response_model=PnLReportResponse)
async def get_pnl_report(
    start_date: date = Query(..., alias="start_date"),
    end_date: date = Query(..., alias="end_date"),
    group_by: str = Query("day", alias="group_by"),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID | None = Depends(get_tenant_filter),
    user: User = Depends(require_permission(Permission.FINANCE_REPORTS))
):
    """Get PnL report for a period."""
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant ID is required"
        )
    
    service = PnLService(db)
    report = await service.generate_pnl_report(tenant_id, start_date, end_date, group_by)
    return PnLReportResponse(**report)
