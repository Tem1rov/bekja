"""Orders router."""

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.permissions import require_permission, Permission
from app.database import get_db
from .schemas import OrderResponse, OrderCreate, OrderUpdate, OrderStatus
from .service import OrderService
from app.modules.warehouse.service import ReservationService

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=list[OrderResponse])
async def list_orders(
    status: OrderStatus | None = None,
    user=Depends(require_permission(Permission.ORDERS_VIEW)),
    db: AsyncSession = Depends(get_db)
):
    """List orders for current tenant."""
    service = OrderService(db)
    orders = await service.list_orders(user.tenant_id, status)
    return orders


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    data: OrderCreate,
    user=Depends(require_permission(Permission.ORDERS_CREATE)),
    db: AsyncSession = Depends(get_db)
):
    """Create a new order."""
    # Использовать tenant_id из пользователя, если не указан в запросе
    tenant_id = data.tenant_id if data.tenant_id else user.tenant_id
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant ID is required"
        )
    
    service = OrderService(db)
    try:
        order = await service.create_order(tenant_id, data)
        return order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{id}", response_model=OrderResponse)
async def get_order(
    id: UUID,
    user=Depends(require_permission(Permission.ORDERS_VIEW)),
    db: AsyncSession = Depends(get_db)
):
    """Get order by ID."""
    service = OrderService(db)
    order = await service.get_order(id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Проверка доступа к тенанту
    if user.role.name != "admin" and order.tenant_id != user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return order


@router.put("/{id}", response_model=OrderResponse)
async def update_order(
    id: UUID,
    data: OrderUpdate,
    user=Depends(require_permission(Permission.ORDERS_EDIT)),
    db: AsyncSession = Depends(get_db)
):
    """Update order."""
    service = OrderService(db)
    order = await service.get_order(id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Проверка доступа к тенанту
    if user.role.name != "admin" and order.tenant_id != user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Обновить статус, если указан
    if data.status and data.status != order.status:
        order = await service.update_status(id, data.status, user.id)
    
    # Обновить другие поля
    for key, value in data.model_dump(exclude_unset=True, exclude={"status"}).items():
        if value is not None:
            setattr(order, key, value)
    
    await db.commit()
    await db.refresh(order)
    return order


@router.post("/{id}/reserve", response_model=dict)
async def reserve_order(
    id: UUID,
    user=Depends(require_permission(Permission.ORDERS_EDIT)),
    db: AsyncSession = Depends(get_db)
):
    """Reserve inventory for order using FIFO/FEFO."""
    service = OrderService(db)
    order = await service.get_order(id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Проверка доступа к тенанту
    if user.role.name != "admin" and order.tenant_id != user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    reservation_service = ReservationService(db)
    try:
        reservations = await reservation_service.reserve_for_order(id)
        
        # Обновить статус заказа на CONFIRMED
        order = await service.update_status(id, OrderStatus.CONFIRMED, user.id)
        
        return {
            "order_id": str(id),
            "status": "reserved",
            "reserved_items": len(reservations),
            "reserved_at": order.confirmed_at.isoformat() if order.confirmed_at else None
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{id}/ship", response_model=OrderResponse)
async def ship_order(
    id: UUID,
    user=Depends(require_permission(Permission.ORDERS_EDIT)),
    db: AsyncSession = Depends(get_db)
):
    """Ship order (fulfill reservations and write off inventory)."""
    service = OrderService(db)
    order = await service.get_order(id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Проверка доступа к тенанту
    if user.role.name != "admin" and order.tenant_id != user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    reservation_service = ReservationService(db)
    try:
        # Списать товар при отгрузке
        await reservation_service.fulfill_reservations(id)
        
        # Обновить статус заказа на SHIPPED
        order = await service.update_status(id, OrderStatus.SHIPPED, user.id)
        
        return order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{id}/cancel", response_model=OrderResponse)
async def cancel_order(
    id: UUID,
    reason: str,
    user=Depends(require_permission(Permission.ORDERS_EDIT)),
    db: AsyncSession = Depends(get_db)
):
    """Cancel order and release reservations."""
    service = OrderService(db)
    order = await service.get_order(id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Проверка доступа к тенанту
    if user.role.name != "admin" and order.tenant_id != user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        order = await service.cancel_order(id, reason, user.id)
        return order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
