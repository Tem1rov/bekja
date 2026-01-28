"""Order service."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from app.models import Order, OrderItem, OrderStatus, OrderHistory
from .schemas import OrderCreate


class OrderService:
    """Service for order operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def list_orders(self, tenant_id: UUID, status: OrderStatus | None = None) -> list[Order]:
        """List orders for a tenant, optionally filtered by status."""
        query = select(Order).where(Order.tenant_id == tenant_id)
        if status:
            query = query.where(Order.status == status)
        query = query.order_by(Order.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_order(self, order_id: UUID) -> Order | None:
        """Get order by ID with items."""
        result = await self.db.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.id == order_id)
        )
        return result.scalar_one_or_none()
    
    async def create_order(self, tenant_id: UUID, data: OrderCreate) -> Order:
        """Create a new order with items."""
        # Генерация номера заказа, если не указан
        order_number = data.order_number
        if not order_number:
            order_number = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        order = Order(
            tenant_id=tenant_id,
            order_number=order_number,
            external_id=data.external_id,
            source=data.source or "manual",
            status=OrderStatus.NEW,
            customer_name=data.customer_name,
            customer_phone=data.customer_phone,
            customer_email=data.customer_email,
            delivery_address=data.delivery_address,
            delivery_method=data.delivery_method,
            total_amount=Decimal("0"),
            notes=data.notes
        )
        self.db.add(order)
        await self.db.flush()  # Получить ID заказа
        
        # Вычислить себестоимость товара для каждого item
        total = Decimal(0)
        cost_of_goods = Decimal(0)
        
        for item_data in data.items:
            # Если cost_price не указан, получить из продукта
            cost_price = item_data.cost_price
            if cost_price is None:
                from app.models import Product
                product = await self.db.get(Product, item_data.product_id)
                if product:
                    cost_price = product.cost_price
                else:
                    cost_price = Decimal(0)
            
            item = OrderItem(
                order_id=order.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                price=item_data.price,
                cost_price=cost_price
            )
            total += item.price * item.quantity
            cost_of_goods += cost_price * item.quantity
            self.db.add(item)
        
        order.total_amount = total
        order.cost_of_goods = cost_of_goods
        
        await self.db.commit()
        await self.db.refresh(order)
        return order
    
    async def update_status(
        self, 
        order_id: UUID, 
        new_status: OrderStatus, 
        user_id: UUID
    ) -> Order:
        """Update order status and save history."""
        order = await self.get_order(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        old_status = order.status
        order.status = new_status
        
        # Сохранить в историю
        history = OrderHistory(
            order_id=order_id,
            old_status=old_status,
            new_status=new_status,
            changed_by=user_id,
            changed_at=datetime.utcnow()
        )
        self.db.add(history)
        
        # Обновить timestamps
        if new_status == OrderStatus.CONFIRMED:
            order.confirmed_at = datetime.utcnow()
        elif new_status == OrderStatus.PICKING:
            order.picked_at = datetime.utcnow()
        elif new_status == OrderStatus.SHIPPED:
            order.shipped_at = datetime.utcnow()
        elif new_status == OrderStatus.DELIVERED:
            order.delivered_at = datetime.utcnow()
        elif new_status == OrderStatus.CANCELLED:
            order.cancelled_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(order)
        return order
    
    async def cancel_order(
        self, 
        order_id: UUID, 
        reason: str, 
        user_id: UUID
    ) -> Order:
        """Cancel order and release reservations."""
        order = await self.get_order(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        if order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
            raise ValueError("Cannot cancel shipped or delivered order")
        
        old_status = order.status
        order.status = OrderStatus.CANCELLED
        order.cancellation_reason = reason
        order.cancelled_at = datetime.utcnow()
        
        # Сохранить в историю
        history = OrderHistory(
            order_id=order_id,
            old_status=old_status,
            new_status=OrderStatus.CANCELLED,
            changed_by=user_id,
            changed_at=datetime.utcnow()
        )
        self.db.add(history)
        
        # Снять резервы (импорт внутри метода, чтобы избежать циклических зависимостей)
        from app.modules.warehouse.service import ReservationService
        reservation_service = ReservationService(self.db)
        await reservation_service.release_reservations(order_id)
        
        await self.db.commit()
        await self.db.refresh(order)
        return order
