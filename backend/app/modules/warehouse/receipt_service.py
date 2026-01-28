"""Receipt service."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from datetime import datetime

from app.models import Receipt, ReceiptItem, Inventory
from .schemas import ReceiptCreate


class ReceiptService:
    """Service for receipt management."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_receipt(self, tenant_id: UUID, data: ReceiptCreate, created_by: UUID) -> Receipt:
        """Create receipt and post inventory."""
        receipt = Receipt(
            tenant_id=tenant_id,
            receipt_number=f"RCP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            status="completed",
            created_by=created_by
        )
        self.db.add(receipt)
        await self.db.flush()
        
        for item in data.items:
            # Create ReceiptItem
            receipt_item = ReceiptItem(
                receipt_id=receipt.id,
                product_id=item.product_id,
                received_quantity=item.quantity,
                cell_id=item.cell_id,
                lot_number=item.batch_number,
                expiry_date=item.expiry_date
            )
            self.db.add(receipt_item)
            
            # Update or create Inventory
            # Search by tenant_id, product_id, cell_id, and batch_number (lot_number)
            query = select(Inventory).where(
                Inventory.tenant_id == tenant_id,
                Inventory.product_id == item.product_id,
                Inventory.cell_id == item.cell_id
            )
            
            # Handle NULL lot_number matching
            if item.batch_number:
                query = query.where(Inventory.lot_number == item.batch_number)
            else:
                query = query.where(Inventory.lot_number.is_(None))
            
            existing = await self.db.execute(query)
            inventory = existing.scalar_one_or_none()
            
            if inventory:
                inventory.quantity += item.quantity
            else:
                inventory = Inventory(
                    tenant_id=tenant_id,
                    product_id=item.product_id,
                    cell_id=item.cell_id,
                    quantity=item.quantity,
                    lot_number=item.batch_number,
                    expiry_date=item.expiry_date,
                    received_at=datetime.utcnow()
                )
                self.db.add(inventory)
        
        await self.db.commit()
        await self.db.refresh(receipt)
        return receipt
