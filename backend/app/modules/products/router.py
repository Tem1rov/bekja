"""Products router."""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel

from app.auth.permissions import require_permission, Permission
from app.database import get_db
from .schemas import ProductResponse, ProductCreate, ProductUpdate, ProductImportResponse
from .service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


class CostUpdateRequest(BaseModel):
    """Request schema for updating product cost."""
    new_cost: Decimal
    reason: str


@router.get("", response_model=list[ProductResponse])
async def list_products(
    user=Depends(require_permission(Permission.PRODUCTS_VIEW)),
    db: AsyncSession = Depends(get_db)
):
    """List products. Filtered by tenant."""
    if not user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant ID required"
        )
    service = ProductService(db)
    products = await service.list_products(user.tenant_id)
    return [ProductResponse.model_validate(p) for p in products]


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    user=Depends(require_permission(Permission.PRODUCTS_CREATE)),
    db: AsyncSession = Depends(get_db)
):
    """Create product."""
    if not user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant ID required"
        )
    # Tenant isolation: use user's tenant_id
    service = ProductService(db)
    product = await service.create_product(user.tenant_id, data)
    return ProductResponse.model_validate(product)


@router.get("/{id}", response_model=ProductResponse)
async def get_product(
    id: UUID,
    user=Depends(require_permission(Permission.PRODUCTS_VIEW)),
    db: AsyncSession = Depends(get_db)
):
    """Get product by ID."""
    service = ProductService(db)
    product = await service.get_product(id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    # Tenant isolation: check if product belongs to user's tenant
    if user.role.name != "admin" and product.tenant_id != user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Product not found"
        )
    return ProductResponse.model_validate(product)


@router.put("/{id}", response_model=ProductResponse)
async def update_product(
    id: UUID,
    data: ProductUpdate,
    user=Depends(require_permission(Permission.PRODUCTS_EDIT)),
    db: AsyncSession = Depends(get_db)
):
    """Update product."""
    service = ProductService(db)
    # Tenant isolation: check if product belongs to user's tenant
    product = await service.get_product(id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if user.role.name != "admin" and product.tenant_id != user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update product from different tenant"
        )
    
    try:
        updated_product = await service.update_product(id, data)
        return ProductResponse.model_validate(updated_product)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/import", response_model=ProductImportResponse)
async def import_products(
    file: UploadFile = File(...),
    user=Depends(require_permission(Permission.PRODUCTS_CREATE)),
    db: AsyncSession = Depends(get_db)
):
    """Import products from CSV file."""
    if not user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant ID required"
        )
    service = ProductService(db)
    result = await service.import_from_csv(user.tenant_id, file)
    return ProductImportResponse(
        imported=result["created"],
        updated=result["updated"],
        failed=result["failed"],
        errors=[f"Row {e['row']}: {e['error']}" for e in result["errors"]]
    )


@router.post("/{id}/cost", response_model=ProductResponse)
async def update_cost_price(
    id: UUID,
    data: CostUpdateRequest,
    user=Depends(require_permission(Permission.PRODUCTS_EDIT)),
    db: AsyncSession = Depends(get_db)
):
    """Update product cost price and save history."""
    service = ProductService(db)
    # Tenant isolation: check if product belongs to user's tenant
    product = await service.get_product(id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if user.role.name != "admin" and product.tenant_id != user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update product from different tenant"
        )
    
    try:
        updated_product = await service.update_cost_price(id, data.new_cost, data.reason)
        return ProductResponse.model_validate(updated_product)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_product(
    id: UUID,
    user=Depends(require_permission(Permission.PRODUCTS_EDIT)),
    db: AsyncSession = Depends(get_db)
):
    """Deactivate product."""
    service = ProductService(db)
    # Tenant isolation: check if product belongs to user's tenant
    product = await service.get_product(id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if user.role.name != "admin" and product.tenant_id != user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot deactivate product from different tenant"
        )
    
    try:
        await service.deactivate_product(id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
