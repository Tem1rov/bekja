"""Integrations router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import select

from app.auth.permissions import require_permission, Permission
from app.database import get_db
from app.models import Integration, SyncLog
from .schemas import IntegrationResponse, IntegrationCreate, IntegrationUpdate, SyncResponse
from .service import IntegrationService

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("", response_model=list[IntegrationResponse])
async def list_integrations(
    user=Depends(require_permission(Permission.WAREHOUSE_VIEW)),
    db: AsyncSession = Depends(get_db)
):
    """List integrations for current tenant."""
    query = select(Integration)
    if user.tenant_id:
        query = query.where(Integration.tenant_id == user.tenant_id)
    
    result = await db.execute(query)
    integrations = result.scalars().all()
    return [IntegrationResponse.model_validate(i) for i in integrations]


@router.post("", response_model=IntegrationResponse)
async def create_integration(
    data: IntegrationCreate,
    user=Depends(require_permission(Permission.WAREHOUSE_MANAGE)),
    db: AsyncSession = Depends(get_db)
):
    """Create a new integration."""
    # Использовать tenant_id из пользователя, если не указан
    tenant_id = data.tenant_id if data.tenant_id else user.tenant_id
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant ID is required"
        )
    
    # Для MVP: сохраняем api_key как есть (в продакшене нужно шифровать)
    integration = Integration(
        tenant_id=tenant_id,
        marketplace=data.marketplace,
        name=data.name,
        api_key_encrypted=data.api_key,  # В продакшене нужно шифровать
        api_secret_encrypted=data.api_secret,  # В продакшене нужно шифровать
        settings=data.settings,
        sync_interval=data.sync_interval,
        is_active=data.is_active
    )
    db.add(integration)
    await db.commit()
    await db.refresh(integration)
    
    return IntegrationResponse.model_validate(integration)


@router.post("/{id}/sync", response_model=SyncResponse)
async def sync_integration(
    id: UUID,
    user=Depends(require_permission(Permission.WAREHOUSE_MANAGE)),
    db: AsyncSession = Depends(get_db)
):
    """Запустить синхронизацию заказов из маркетплейса."""
    service = IntegrationService(db)
    
    try:
        result = await service.sync_orders(id)
        
        # Получить последний sync log
        sync_log_result = await db.execute(
            select(SyncLog)
            .where(SyncLog.integration_id == id)
            .order_by(SyncLog.started_at.desc())
            .limit(1)
        )
        sync_log = sync_log_result.scalar_one_or_none()
        
        if sync_log:
            return SyncResponse(
                sync_id=sync_log.id,
                integration_id=id,
                status=sync_log.status,
                started_at=sync_log.started_at,
                items_processed=sync_log.items_processed,
                items_created=sync_log.items_created,
                items_updated=sync_log.items_updated,
                items_failed=sync_log.items_failed
            )
        else:
            return SyncResponse(
                sync_id=uuid4(),
                integration_id=id,
                status="success",
                started_at=datetime.utcnow(),
                items_processed=result.get("total_processed", 0),
                items_created=result.get("created", 0),
                items_updated=result.get("updated", 0),
                items_failed=len(result.get("errors", []))
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
