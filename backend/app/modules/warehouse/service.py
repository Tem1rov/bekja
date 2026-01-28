"""Warehouse services."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from datetime import datetime

from app.models import Warehouse, Zone, Rack, Cell, Inventory, Reservation, Order, OrderItem
from .schemas import ZoneCreate, RackCreate


class WarehouseService:
    """Service for warehouse topology management."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_warehouse(self, warehouse_id: UUID) -> Warehouse | None:
        """Get warehouse with zones."""
        result = await self.db.execute(
            select(Warehouse)
            .options(selectinload(Warehouse.zones))
            .where(Warehouse.id == warehouse_id)
        )
        return result.scalar_one_or_none()
    
    async def create_zone(self, warehouse_id: UUID, data: ZoneCreate) -> Zone:
        """Create a new zone in warehouse."""
        zone = Zone(warehouse_id=warehouse_id, **data.model_dump())
        self.db.add(zone)
        await self.db.commit()
        await self.db.refresh(zone)
        return zone
    
    async def create_rack(self, zone_id: UUID, data: RackCreate) -> Rack:
        """Create a new rack in zone."""
        rack = Rack(zone_id=zone_id, **data.model_dump())
        self.db.add(rack)
        await self.db.commit()
        await self.db.refresh(rack)
        return rack
    
    async def create_cells_bulk(self, rack_id: UUID, prefix: str, count: int) -> list[Cell]:
        """Bulk create cells: A1-01, A1-02, ..., A1-50."""
        cells = []
        for i in range(1, count + 1):
            cell = Cell(
                rack_id=rack_id,
                code=f"{prefix}-{i:02d}",
                size="M",
                max_weight=100
            )
            cells.append(cell)
            self.db.add(cell)
        await self.db.commit()
        # Refresh all cells
        for cell in cells:
            await self.db.refresh(cell)
        return cells
    
    async def get_cell(self, cell_id: UUID) -> Cell | None:
        """Get cell by ID."""
        return await self.db.get(Cell, cell_id)
    
    async def list_cells(self, warehouse_id: UUID | None = None) -> list[Cell]:
        """List cells, optionally filtered by warehouse."""
        query = select(Cell).options(
            selectinload(Cell.rack).selectinload(Rack.zone).selectinload(Zone.warehouse)
        )
        if warehouse_id:
            query = query.join(Cell.rack).join(Rack.zone).where(Zone.warehouse_id == warehouse_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())


class InventoryService:
    """Service for inventory management."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_inventory(self, tenant_id: UUID, product_id: UUID | None = None) -> list[Inventory]:
        """Get inventory for tenant, optionally filtered by product."""
        query = select(Inventory).where(Inventory.tenant_id == tenant_id)
        if product_id:
            query = query.where(Inventory.product_id == product_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_available_quantity(self, tenant_id: UUID, product_id: UUID) -> int:
        """Get available quantity = quantity - reserved_quantity."""
        result = await self.db.execute(
            select(Inventory).where(
                Inventory.tenant_id == tenant_id,
                Inventory.product_id == product_id
            )
        )
        inventories = result.scalars().all()
        return sum(inv.quantity - inv.reserved_quantity for inv in inventories)


class ReservationService:
    """Service for order reservations with FIFO/FEFO."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def reserve_for_order(self, order_id: UUID) -> list[Reservation]:
        """Reserve inventory for order items using FIFO/FEFO."""
        order = await self.db.get(Order, order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        reservations = []
        
        # Загрузить items с продуктами
        result = await self.db.execute(
            select(OrderItem)
            .where(OrderItem.order_id == order_id)
        )
        items = result.scalars().all()
        
        for item in items:
            # Получить доступные остатки с сортировкой FIFO/FEFO
            query = select(Inventory).where(
                Inventory.tenant_id == order.tenant_id,
                Inventory.product_id == item.product_id,
                Inventory.quantity > Inventory.reserved_quantity
            )
            
            # FEFO: сначала по сроку годности (если есть), затем FIFO по дате поступления
            query = query.order_by(
                Inventory.expiry_date.nulls_last(),
                Inventory.received_at
            )
            
            result = await self.db.execute(query)
            inventories = result.scalars().all()
            
            remaining = item.quantity
            for inv in inventories:
                if remaining <= 0:
                    break
                
                available = inv.quantity - inv.reserved_quantity
                to_reserve = min(available, remaining)
                
                if to_reserve <= 0:
                    continue
                
                # Создать резерв
                reservation = Reservation(
                    order_id=order_id,
                    order_item_id=item.id,
                    inventory_id=inv.id,
                    product_id=item.product_id,
                    cell_id=inv.cell_id,
                    quantity=to_reserve
                )
                self.db.add(reservation)
                reservations.append(reservation)
                
                # Увеличить reserved_quantity
                inv.reserved_quantity += to_reserve
                item.reserved_quantity += to_reserve
                remaining -= to_reserve
            
            # Если осталось нерезервированное количество
            if remaining > 0:
                item.shortage = remaining
        
        await self.db.commit()
        return reservations
    
    async def release_reservations(self, order_id: UUID) -> None:
        """Release reservations when order is cancelled."""
        result = await self.db.execute(
            select(Reservation).where(Reservation.order_id == order_id)
        )
        reservations = result.scalars().all()
        
        for res in reservations:
            inv = await self.db.get(Inventory, res.inventory_id)
            if inv:
                inv.reserved_quantity -= res.quantity
            
            # Обновить reserved_quantity в OrderItem
            item = await self.db.get(OrderItem, res.order_item_id)
            if item:
                item.reserved_quantity -= res.quantity
            
            await self.db.delete(res)
        
        await self.db.commit()
    
    async def fulfill_reservations(self, order_id: UUID) -> None:
        """Fulfill reservations when order is shipped (write off inventory)."""
        result = await self.db.execute(
            select(Reservation).where(Reservation.order_id == order_id)
        )
        reservations = result.scalars().all()
        
        for res in reservations:
            inv = await self.db.get(Inventory, res.inventory_id)
            if inv:
                inv.quantity -= res.quantity
                inv.reserved_quantity -= res.quantity
            
            # Обновить picked_quantity в OrderItem
            item = await self.db.get(OrderItem, res.order_item_id)
            if item:
                item.picked_quantity += res.quantity
            
            res.fulfilled_at = datetime.utcnow()
            res.status = "fulfilled"
        
        await self.db.commit()
