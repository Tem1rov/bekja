"""Warehouse cells, inventory, receipts, transfers router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.auth.permissions import require_permission, Permission
from app.models import User
from .schemas import (
    InventoryResponse,
    ReceiptCreate,
    ReceiptResponse,
    TransferCreate,
    TransferResponse
)
from .service import InventoryService
from .receipt_service import ReceiptService
from .transfer_service import TransferService

router = APIRouter(tags=["warehouse"])


@router.get("/inventory", response_model=list[InventoryResponse])
async def list_inventory(
    product_id: UUID | None = None,
    user: User = Depends(require_permission(Permission.WAREHOUSE_INVENTORY)),
    db: AsyncSession = Depends(get_db)
):
    """List inventory for current tenant."""
    if not user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to a tenant"
        )
    service = InventoryService(db)
    inventories = await service.get_inventory(user.tenant_id, product_id)
    return [InventoryResponse.model_validate(inv) for inv in inventories]


@router.post("/receipts", response_model=ReceiptResponse)
async def create_receipt(
    data: ReceiptCreate,
    user: User = Depends(require_permission(Permission.WAREHOUSE_INVENTORY)),
    db: AsyncSession = Depends(get_db)
):
    """Create receipt and post inventory."""
    if not user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to a tenant"
        )
    service = ReceiptService(db)
    try:
        receipt = await service.create_receipt(user.tenant_id, data, user.id)
        return ReceiptResponse.model_validate(receipt)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/transfers", response_model=TransferResponse)
async def create_transfer(
    data: TransferCreate,
    user: User = Depends(require_permission(Permission.WAREHOUSE_MANAGE)),
    db: AsyncSession = Depends(get_db)
):
    """Create transfer between cells."""
    if not user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to a tenant"
        )
    service = TransferService(db)
    try:
        transfer = await service.create_transfer(user.tenant_id, data, user.id)
        return TransferResponse.model_validate(transfer)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
