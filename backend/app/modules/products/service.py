"""Product service."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from decimal import Decimal
import csv
import io
from fastapi import UploadFile

from app.models import Product, ProductCostHistory
from .schemas import ProductCreate, ProductUpdate


class ProductService:
    """Service for product operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def list_products(self, tenant_id: UUID, skip: int = 0, limit: int = 100) -> list[Product]:
        """List products for a tenant."""
        result = await self.db.execute(
            select(Product)
            .where(Product.tenant_id == tenant_id, Product.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_product(self, product_id: UUID) -> Product | None:
        """Get product by ID."""
        return await self.db.get(Product, product_id)
    
    async def create_product(self, tenant_id: UUID, data: ProductCreate) -> Product:
        """Create a new product."""
        product = Product(tenant_id=tenant_id, **data.model_dump())
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product
    
    async def update_product(self, product_id: UUID, data: ProductUpdate) -> Product:
        """Update product."""
        product = await self.get_product(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(product, key, value)
        
        await self.db.commit()
        await self.db.refresh(product)
        return product
    
    async def update_cost_price(self, product_id: UUID, new_cost: Decimal, reason: str) -> Product:
        """Update product cost price and save history."""
        product = await self.get_product(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        # Save history
        history = ProductCostHistory(
            product_id=product_id,
            old_cost=product.cost_price,
            new_cost=new_cost,
            reason=reason
        )
        self.db.add(history)
        
        # Update cost
        product.cost_price = new_cost
        await self.db.commit()
        await self.db.refresh(product)
        return product
    
    async def import_from_csv(self, tenant_id: UUID, file: UploadFile) -> dict:
        """Import products from CSV file."""
        content = await file.read()
        reader = csv.DictReader(io.StringIO(content.decode('utf-8')))
        
        created = 0
        updated = 0
        errors = []
        
        for row_num, row in enumerate(reader, start=2):  # Start from 2 (row 1 is header)
            try:
                if not row.get('sku'):
                    errors.append({"row": row_num, "error": "Missing SKU"})
                    continue
                
                # Check if product exists
                result = await self.db.execute(
                    select(Product).where(
                        Product.tenant_id == tenant_id,
                        Product.sku == row['sku']
                    )
                )
                product = result.scalar_one_or_none()
                
                if product:
                    # Update existing product
                    if 'name' in row:
                        product.name = row['name']
                    if 'cost_price' in row:
                        try:
                            product.cost_price = Decimal(row['cost_price'])
                        except (ValueError, TypeError):
                            errors.append({"row": row_num, "error": f"Invalid cost_price: {row.get('cost_price')}"})
                            continue
                    updated += 1
                else:
                    # Create new product
                    try:
                        product = Product(
                            tenant_id=tenant_id,
                            sku=row['sku'],
                            name=row.get('name', ''),
                            cost_price=Decimal(row.get('cost_price', 0))
                        )
                        self.db.add(product)
                        created += 1
                    except (ValueError, TypeError) as e:
                        errors.append({"row": row_num, "error": f"Invalid data: {str(e)}"})
                        continue
            except Exception as e:
                errors.append({"row": row_num, "error": str(e)})
        
        await self.db.commit()
        return {
            "created": created,
            "updated": updated,
            "failed": len(errors),
            "errors": errors
        }
    
    async def deactivate_product(self, product_id: UUID) -> None:
        """Deactivate product."""
        product = await self.get_product(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        product.is_active = False
        await self.db.commit()
