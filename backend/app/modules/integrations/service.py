"""Integration service for marketplace integrations."""

from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal

from app.models import Integration, Order, OrderItem, OrderStatus, Product, SyncLog


class MarketplaceClient(ABC):
    """Abstract base class for marketplace clients."""
    
    @abstractmethod
    async def get_orders(self, since: datetime) -> list[dict]:
        """Get orders from marketplace since given datetime."""
        pass
    
    @abstractmethod
    async def update_order_status(self, order_id: str, status: str) -> bool:
        """Update order status in marketplace."""
        pass


class OzonClient(MarketplaceClient):
    """Ozon marketplace client."""
    
    def __init__(self, client_id: str, api_key: str):
        self.client_id = client_id
        self.api_key = api_key
        self.base_url = "https://api-seller.ozon.ru"
    
    async def get_orders(self, since: datetime) -> list[dict]:
        """Get orders from Ozon (MVP: stub implementation)."""
        # TODO: Реальный API вызов
        # Для MVP - заглушка
        return [
            {
                "external_id": "OZON-123456",
                "status": "awaiting_deliver",
                "customer": {"name": "Иванов И.И.", "phone": "+79001234567"},
                "delivery_address": "г. Москва, ул. Примерная, д. 1",
                "items": [{"sku": "SKU-001", "quantity": 2, "price": 1500}]
            }
        ]
    
    async def update_order_status(self, order_id: str, status: str) -> bool:
        """Update order status in Ozon (MVP: stub implementation)."""
        # TODO: Реальный API вызов
        return True


class WildberriesClient(MarketplaceClient):
    """Wildberries marketplace client."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://suppliers-api.wildberries.ru"
    
    async def get_orders(self, since: datetime) -> list[dict]:
        """Get orders from Wildberries (MVP: stub implementation)."""
        # TODO: Реальный API вызов
        return []
    
    async def update_order_status(self, order_id: str, status: str) -> bool:
        """Update order status in Wildberries (MVP: stub implementation)."""
        # TODO: Реальный API вызов
        return True


class IntegrationService:
    """Service for marketplace integrations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def _get_marketplace_client(self, integration: Integration) -> MarketplaceClient:
        """Create marketplace client from integration."""
        # Для MVP: используем api_key напрямую (в продакшене нужно расшифровывать)
        api_key = integration.api_key_encrypted  # В реальности нужно расшифровать
        api_secret = integration.api_secret_encrypted  # В реальности нужно расшифровать
        
        if integration.marketplace == "ozon":
            # Ozon требует client_id и api_key
            client_id = integration.settings.get("client_id", "")
            return OzonClient(client_id=client_id, api_key=api_key)
        elif integration.marketplace == "wildberries":
            return WildberriesClient(api_key=api_key)
        else:
            raise ValueError(f"Unknown marketplace: {integration.marketplace}")
    
    async def sync_orders(self, integration_id: UUID) -> dict:
        """Синхронизация заказов из маркетплейса."""
        result = await self.db.execute(
            select(Integration).where(Integration.id == integration_id)
        )
        integration = result.scalar_one_or_none()
        
        if not integration:
            raise ValueError(f"Integration {integration_id} not found")
        
        if not integration.is_active:
            raise ValueError(f"Integration {integration_id} is not active")
        
        # Создать клиент маркетплейса
        client = self._get_marketplace_client(integration)
        
        # Получить заказы
        last_sync = integration.last_sync_at or datetime.min.replace(tzinfo=None)
        orders = await client.get_orders(since=last_sync)
        
        created = 0
        updated = 0
        errors = []
        
        for order_data in orders:
            try:
                # Проверить дубликат
                existing_result = await self.db.execute(
                    select(Order).where(
                        Order.external_id == order_data["external_id"],
                        Order.tenant_id == integration.tenant_id
                    )
                )
                existing = existing_result.scalar_one_or_none()
                
                if existing:
                    # Обновить статус (если нужно)
                    updated += 1
                    continue
                
                # Сопоставить SKU
                items = []
                total_amount = Decimal("0")
                
                for item_data in order_data["items"]:
                    product_result = await self.db.execute(
                        select(Product).where(
                            Product.tenant_id == integration.tenant_id,
                            Product.sku == item_data["sku"]
                        )
                    )
                    product = product_result.scalar_one_or_none()
                    
                    if not product:
                        errors.append(f"SKU not found: {item_data['sku']}")
                        continue
                    
                    item_price = Decimal(str(item_data["price"]))
                    item_quantity = item_data["quantity"]
                    total_amount += item_price * item_quantity
                    
                    items.append({
                        "product_id": product.id,
                        "quantity": item_quantity,
                        "price": item_price,
                        "cost_price": product.cost_price
                    })
                
                if not items:
                    errors.append(f"No valid items for order {order_data['external_id']}")
                    continue
                
                # Создать заказ
                order = Order(
                    tenant_id=integration.tenant_id,
                    integration_id=integration.id,
                    external_id=order_data["external_id"],
                    order_number=order_data["external_id"],
                    source=integration.marketplace,
                    status=OrderStatus.NEW,
                    customer_name=order_data.get("customer", {}).get("name"),
                    customer_phone=order_data.get("customer", {}).get("phone"),
                    delivery_address=order_data.get("delivery_address"),
                    total_amount=total_amount
                )
                self.db.add(order)
                await self.db.flush()  # Получить ID заказа
                
                # Создать позиции заказа
                for item_data in items:
                    order_item = OrderItem(
                        order_id=order.id,
                        product_id=item_data["product_id"],
                        quantity=item_data["quantity"],
                        price=item_data["price"],
                        cost_price=item_data["cost_price"]
                    )
                    self.db.add(order_item)
                
                # Обновить cost_of_goods
                order.cost_of_goods = sum(
                    Decimal(str(item["cost_price"])) * item["quantity"]
                    for item in items
                )
                
                created += 1
                
            except Exception as e:
                errors.append(f"Error processing order {order_data.get('external_id', 'unknown')}: {str(e)}")
        
        # Обновить время синхронизации
        integration.last_sync_at = datetime.utcnow()
        integration.last_sync_status = "success" if not errors else "error"
        integration.last_sync_error = "; ".join(errors) if errors else None
        
        # Сохранить лог
        sync_log = SyncLog(
            integration_id=integration_id,
            sync_type="orders",
            status="success" if not errors else "error",
            items_processed=len(orders),
            items_created=created,
            items_updated=updated,
            items_failed=len(errors),
            error_details={"errors": errors} if errors else None,
            completed_at=datetime.utcnow()
        )
        self.db.add(sync_log)
        
        await self.db.commit()
        
        return {
            "created": created,
            "updated": updated,
            "errors": errors,
            "total_processed": len(orders)
        }
