"""Dashboard service."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from datetime import date, datetime
from typing import Optional

from app.models import Order, OrderStatus, Product, Inventory
from app.modules.finance.service import PnLService
from app.modules.notifications.service import AlertService


class DashboardService:
    """Service for dashboard data."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_dashboard_data(self, tenant_id: UUID | None) -> dict:
        """Данные для главного дашборда."""
        today = date.today()
        
        # Заказы сегодня
        orders_query = select(func.count(Order.id)).where(
            func.date(Order.created_at) == today
        )
        if tenant_id:
            orders_query = orders_query.where(Order.tenant_id == tenant_id)
        
        orders_today_result = await self.db.execute(orders_query)
        orders_today = orders_today_result.scalar_one() or 0
        
        # Заказы по статусам
        status_query = select(Order.status, func.count(Order.id)).group_by(Order.status)
        if tenant_id:
            status_query = status_query.where(Order.tenant_id == tenant_id)
        statuses_result = await self.db.execute(status_query)
        orders_by_status = {status.value: count for status, count in statuses_result.all()}
        
        # PnL за сегодня
        pnl_today = {
            "revenue": 0.0,
            "margin": 0.0,
            "margin_percent": 0.0
        }
        
        if tenant_id:
            pnl_service = PnLService(self.db)
            try:
                pnl_report = await pnl_service.generate_pnl_report(tenant_id, today, today)
                pnl_today = {
                    "revenue": pnl_report.get("total_revenue", 0.0),
                    "margin": pnl_report.get("total_margin", 0.0),
                    "margin_percent": pnl_report.get("margin_percent", 0.0)
                }
            except Exception:
                pass  # Если нет данных, используем значения по умолчанию
        
        # Низкие остатки
        low_stock_count = 0
        low_stock_items = []
        
        if tenant_id:
            alert_service = AlertService(self.db)
            try:
                low_stock = await alert_service.check_low_stock_alerts(tenant_id)
                low_stock_count = len(low_stock)
                low_stock_items = low_stock[:5]  # Первые 5
            except Exception:
                pass  # Если нет данных, используем значения по умолчанию
        
        return {
            "orders_today": orders_today,
            "orders_by_status": orders_by_status,
            "pnl_today": pnl_today,
            "low_stock_count": low_stock_count,
            "low_stock_items": low_stock_items
        }
