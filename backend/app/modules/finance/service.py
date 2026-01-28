"""Finance services: TariffService and PnLService."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from uuid import UUID
from datetime import date
from decimal import Decimal

from app.models import (
    Tariff,
    Order,
    OrderItem,
    OrderStatus,
    StorageCharge,
    MarketplaceFee,
    Tenant,
)
from .schemas import TariffUpdate


class TariffService:
    """Service for tariff operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_tariffs(self, tenant_id: UUID) -> Tariff | None:
        """Get tariffs for a tenant."""
        result = await self.db.execute(
            select(Tariff).where(Tariff.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()
    
    async def update_tariffs(self, tenant_id: UUID, data: TariffUpdate) -> Tariff:
        """Create or update tariffs for a tenant."""
        tariff = await self.get_tariffs(tenant_id)
        if not tariff:
            tariff = Tariff(tenant_id=tenant_id)
            self.db.add(tariff)
        
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(tariff, key, value)
        
        await self.db.commit()
        await self.db.refresh(tariff)
        return tariff


class PnLService:
    """Service for PnL calculations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def calculate_order_pnl(self, order_id: UUID) -> dict:
        """Calculate PnL for an order."""
        result = await self.db.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        # Get tariffs
        tariff_result = await self.db.execute(
            select(Tariff).where(Tariff.tenant_id == order.tenant_id)
        )
        tariff = tariff_result.scalar_one_or_none()
        
        # Revenue
        revenue = float(order.total_amount)
        
        # Cost of goods
        cost_of_goods = sum(
            float(item.cost_price * item.quantity) for item in order.items
        )
        
        # Processing cost
        processing_cost = float(tariff.processing_rate) if tariff else 0
        
        # Storage cost
        storage_cost = await self._calculate_storage_cost(order)
        
        # Marketplace fee
        marketplace_fee = await self._get_marketplace_fee(order)
        
        # Total expenses
        total_expenses = cost_of_goods + processing_cost + storage_cost + marketplace_fee
        
        # Margin
        margin = revenue - total_expenses
        margin_percent = (margin / revenue * 100) if revenue > 0 else 0
        
        return {
            "order_id": str(order_id),
            "revenue": revenue,
            "cost_of_goods": cost_of_goods,
            "processing_cost": processing_cost,
            "storage_cost": storage_cost,
            "marketplace_fee": marketplace_fee,
            "total_expenses": total_expenses,
            "margin": margin,
            "margin_percent": round(margin_percent, 2)
        }
    
    async def _calculate_storage_cost(self, order: Order) -> float:
        """Calculate storage costs (proportional to days)."""
        if not order.shipped_at:
            return 0
        
        storage_charges = await self.db.execute(
            select(StorageCharge).where(
                StorageCharge.tenant_id == order.tenant_id,
                StorageCharge.order_id == order.id
            )
        )
        charges = storage_charges.scalars().all()
        return sum(float(c.amount) for c in charges)
    
    async def _get_marketplace_fee(self, order: Order) -> float:
        """Get marketplace fee."""
        if not order.integration_id:
            return 0
        
        fee_result = await self.db.execute(
            select(MarketplaceFee).where(
                MarketplaceFee.integration_id == order.integration_id,
                MarketplaceFee.is_active == True
            )
        )
        fee = fee_result.scalar_one_or_none()
        if not fee:
            return 0
        
        if fee.fee_type == "percent":
            return float(order.total_amount * fee.fee_value / 100)
        return float(fee.fee_value)
    
    async def generate_pnl_report(
        self,
        tenant_id: UUID,
        start_date: date,
        end_date: date,
        group_by: str = "day"
    ) -> dict:
        """Generate PnL report for a period."""
        orders_result = await self.db.execute(
            select(Order).where(
                Order.tenant_id == tenant_id,
                Order.created_at >= start_date,
                Order.created_at <= end_date,
                Order.status != OrderStatus.CANCELLED
            )
        )
        orders = orders_result.scalars().all()
        
        total_revenue = 0
        total_expenses = 0
        order_pnls = []
        
        for order in orders:
            pnl = await self.calculate_order_pnl(order.id)
            order_pnls.append(pnl)
            total_revenue += pnl["revenue"]
            total_expenses += pnl["total_expenses"]
        
        return {
            "period": {"start": str(start_date), "end": str(end_date)},
            "total_revenue": total_revenue,
            "total_expenses": total_expenses,
            "total_margin": total_revenue - total_expenses,
            "margin_percent": round((total_revenue - total_expenses) / total_revenue * 100, 2) if total_revenue else 0,
            "orders_count": len(orders),
            "orders": order_pnls
        }
