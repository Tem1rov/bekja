"""Notification and Alert services."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from datetime import datetime

from app.models import Notification, User, Product, Inventory


class NotificationService:
    """Service for notification operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_notification(
        self,
        user_id: UUID,
        notification_type: str,
        title: str,
        message: str,
        data: dict = None
    ) -> Notification:
        """Create a notification."""
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            data=data or {},
            is_read=False
        )
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification
    
    async def get_unread_count(self, user_id: UUID) -> int:
        """Get count of unread notifications for a user."""
        result = await self.db.execute(
            select(func.count(Notification.id)).where(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        )
        return result.scalar_one() or 0
    
    async def mark_as_read(self, notification_id: UUID) -> Notification:
        """Mark a notification as read."""
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()
        if not notification:
            raise ValueError(f"Notification {notification_id} not found")
        
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(notification)
        return notification
    
    async def list_notifications(
        self,
        user_id: UUID,
        is_read: bool | None = None,
        limit: int = 50,
        offset: int = 0
    ) -> list[Notification]:
        """List notifications for a user."""
        query = select(Notification).where(Notification.user_id == user_id)
        if is_read is not None:
            query = query.where(Notification.is_read == is_read)
        query = query.order_by(Notification.created_at.desc()).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())


class AlertService:
    """Service for low stock alerts."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.notification_service = NotificationService(db)
    
    async def check_low_stock_alerts(self, tenant_id: UUID) -> list[dict]:
        """Check products with low stock levels."""
        products_result = await self.db.execute(
            select(Product).where(
                Product.tenant_id == tenant_id,
                Product.min_stock_level > 0,
                Product.is_active == True
            )
        )
        products = products_result.scalars().all()
        
        alerts = []
        for product in products:
            # Get current stock
            inventory_result = await self.db.execute(
                select(func.sum(Inventory.quantity - Inventory.reserved_quantity))
                .where(
                    Inventory.tenant_id == tenant_id,
                    Inventory.product_id == product.id
                )
            )
            current_stock = inventory_result.scalar_one() or 0
            
            if current_stock < product.min_stock_level:
                # Get tenant managers
                users_result = await self.db.execute(
                    select(User).where(
                        User.tenant_id == tenant_id,
                        User.is_active == True
                    )
                )
                users = users_result.scalars().all()
                
                # Create notifications for all users
                for user in users:
                    await self.notification_service.create_notification(
                        user_id=user.id,
                        notification_type="low_stock",
                        title="Низкий остаток товара",
                        message=f"Товар {product.name} (SKU: {product.sku}) — остаток {current_stock} шт. (мин: {product.min_stock_level})",
                        data={
                            "product_id": str(product.id),
                            "current_stock": current_stock,
                            "min_stock_level": product.min_stock_level
                        }
                    )
                
                alerts.append({
                    "product_id": str(product.id),
                    "sku": product.sku,
                    "current_stock": current_stock,
                    "min_level": product.min_stock_level
                })
        
        return alerts
