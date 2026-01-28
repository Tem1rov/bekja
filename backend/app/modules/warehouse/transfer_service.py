"""Transfer service."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.models import Transfer, Inventory
from .schemas import TransferCreate


class TransferService:
    """Service for transfer management."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_transfer(self, tenant_id: UUID, data: TransferCreate, created_by: UUID) -> Transfer:
        """Transfer goods between cells."""
        # Check availability in source cell
        query = select(Inventory).where(
            Inventory.tenant_id == tenant_id,
            Inventory.product_id == data.product_id,
            Inventory.cell_id == data.source_cell_id
        )
        
        # Handle NULL lot_number matching
        if data.lot_number:
            query = query.where(Inventory.lot_number == data.lot_number)
        else:
            query = query.where(Inventory.lot_number.is_(None))
        
        source_inv = await self.db.execute(query)
        source = source_inv.scalar_one_or_none()
        
        if not source or source.quantity < data.quantity:
            raise ValueError("Insufficient quantity in source cell")
        
        # Decrease in source
        source.quantity -= data.quantity
        
        # Increase or create in target
        target_query = select(Inventory).where(
            Inventory.tenant_id == tenant_id,
            Inventory.product_id == data.product_id,
            Inventory.cell_id == data.target_cell_id
        )
        
        if data.lot_number:
            target_query = target_query.where(Inventory.lot_number == data.lot_number)
        else:
            target_query = target_query.where(Inventory.lot_number.is_(None))
        
        target_inv = await self.db.execute(target_query)
        target = target_inv.scalar_one_or_none()
        
        if target:
            target.quantity += data.quantity
        else:
            # Get source inventory details for new target inventory
            target = Inventory(
                tenant_id=tenant_id,
                product_id=data.product_id,
                cell_id=data.target_cell_id,
                quantity=data.quantity,
                lot_number=source.lot_number,
                expiry_date=source.expiry_date,
                received_at=source.received_at
            )
            self.db.add(target)
        
        # Create transfer document
        transfer = Transfer(
            tenant_id=tenant_id,
            product_id=data.product_id,
            source_cell_id=data.source_cell_id,
            target_cell_id=data.target_cell_id,
            quantity=data.quantity,
            lot_number=data.lot_number,
            created_by=created_by
        )
        self.db.add(transfer)
        
        await self.db.commit()
        await self.db.refresh(transfer)
        return transfer
