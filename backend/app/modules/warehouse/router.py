"""Warehouse router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.auth.permissions import require_permission, Permission
from app.models import User
from .schemas import (
    WarehouseResponse,
    ZoneResponse,
    ZoneCreate,
    RackCreate,
    RackResponse,
    CellResponse
)
from .service import WarehouseService

router = APIRouter(prefix="/warehouses", tags=["warehouse"])


@router.get("", response_model=list[WarehouseResponse])
async def list_warehouses(user=Depends(require_permission(Permission.WAREHOUSE_VIEW))):
    """TODO: Реализовать получение из БД"""
    return [
        WarehouseResponse(
            id=uuid4(),
            name="Main Warehouse",
            address="123 Warehouse St, City",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        WarehouseResponse(
            id=uuid4(),
            name="Secondary Warehouse",
            address="456 Storage Ave, Town",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    ]


@router.get("/{id}/zones", response_model=list[ZoneResponse])
async def list_zones(
    id: UUID,
    user: User = Depends(require_permission(Permission.WAREHOUSE_VIEW)),
    db: AsyncSession = Depends(get_db)
):
    """List zones in warehouse."""
    service = WarehouseService(db)
    warehouse = await service.get_warehouse(id)
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )
    return [ZoneResponse.model_validate(zone) for zone in warehouse.zones]


@router.post("/{id}/zones", response_model=ZoneResponse)
async def create_zone(
    id: UUID,
    data: ZoneCreate,
    user: User = Depends(require_permission(Permission.WAREHOUSE_MANAGE)),
    db: AsyncSession = Depends(get_db)
):
    """Create a new zone in warehouse."""
    service = WarehouseService(db)
    warehouse = await service.get_warehouse(id)
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )
    zone = await service.create_zone(id, data)
    return ZoneResponse.model_validate(zone)


@router.post("/zones/{zone_id}/racks", response_model=RackResponse)
async def create_rack(
    zone_id: UUID,
    data: RackCreate,
    user: User = Depends(require_permission(Permission.WAREHOUSE_MANAGE)),
    db: AsyncSession = Depends(get_db)
):
    """Create a new rack in zone."""
    service = WarehouseService(db)
    rack = await service.create_rack(zone_id, data)
    return RackResponse.model_validate(rack)


@router.post("/racks/{rack_id}/cells/bulk")
async def create_cells_bulk(
    rack_id: UUID,
    prefix: str,
    count: int,
    user: User = Depends(require_permission(Permission.WAREHOUSE_MANAGE)),
    db: AsyncSession = Depends(get_db)
):
    """Bulk create cells in rack."""
    if count < 1 or count > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Count must be between 1 and 1000"
        )
    service = WarehouseService(db)
    cells = await service.create_cells_bulk(rack_id, prefix, count)
    return {
        "rack_id": rack_id,
        "prefix": prefix,
        "count": len(cells),
        "cells": [CellResponse.model_validate(cell) for cell in cells]
    }


@router.get("/cells", response_model=list[CellResponse])
async def list_cells(
    warehouse_id: UUID | None = None,
    user: User = Depends(require_permission(Permission.WAREHOUSE_VIEW)),
    db: AsyncSession = Depends(get_db)
):
    """List cells, optionally filtered by warehouse."""
    service = WarehouseService(db)
    cells = await service.list_cells(warehouse_id)
    return [CellResponse.model_validate(cell) for cell in cells]
