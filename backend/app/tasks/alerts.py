"""Celery tasks for alerts and periodic calculations."""

from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from uuid import UUID
from datetime import date, datetime, timedelta
from decimal import Decimal

from app.config import settings
from app.models import Tenant, Product, Inventory, StorageCharge, Tariff, Order, OrderItem, Reservation
from app.modules.notifications.service import AlertService


# Create async engine for tasks
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@shared_task(name="app.tasks.alerts.check_low_stock_alerts_task")
def check_low_stock_alerts_task():
    """Periodic check for low stock alerts."""
    import asyncio
    
    async def run_check():
        async with AsyncSessionLocal() as session:
            # Get all active tenants
            result = await session.execute(
                select(Tenant).where(Tenant.is_active == True)
            )
            tenants = result.scalars().all()
            
            total_alerts = 0
            for tenant in tenants:
                alert_service = AlertService(session)
                alerts = await alert_service.check_low_stock_alerts(tenant.id)
                total_alerts += len(alerts)
            
            return f"Checked {len(tenants)} tenants, found {total_alerts} low stock alerts"
    
    return asyncio.run(run_check())


@shared_task(name="app.tasks.alerts.calculate_daily_storage_charges")
def calculate_daily_storage_charges():
    """Calculate daily storage charges for all tenants."""
    import asyncio
    
    async def run_calculation():
        async with AsyncSessionLocal() as session:
            today = date.today()
            
            # Get all active tenants
            tenants_result = await session.execute(
                select(Tenant).where(Tenant.is_active == True)
            )
            tenants = tenants_result.scalars().all()
            
            total_charges = 0
            
            for tenant in tenants:
                # Get tariff for tenant
                tariff_result = await session.execute(
                    select(Tariff).where(Tariff.tenant_id == tenant.id)
                )
                tariff = tariff_result.scalar_one_or_none()
                
                if not tariff or tariff.storage_rate == 0:
                    continue
                
                # Get all active products with inventory
                products_result = await session.execute(
                    select(Product).where(
                        Product.tenant_id == tenant.id,
                        Product.is_active == True
                    )
                )
                products = products_result.scalars().all()
                
                for product in products:
                    # Get current inventory quantity (not reserved)
                    inventory_result = await session.execute(
                        select(
                            Inventory.product_id,
                            (Inventory.quantity - Inventory.reserved_quantity).label("available")
                        ).where(
                            Inventory.tenant_id == tenant.id,
                            Inventory.product_id == product.id
                        )
                    )
                    inventory_data = inventory_result.all()
                    
                    total_available = sum(row.available for row in inventory_data if row.available > 0)
                    
                    if total_available > 0:
                        # Calculate charge amount
                        # Assuming storage_rate is per unit per day
                        charge_amount = Decimal(str(total_available)) * tariff.storage_rate
                        
                        # Check if charge already exists for today
                        existing_result = await session.execute(
                            select(StorageCharge).where(
                                StorageCharge.tenant_id == tenant.id,
                                StorageCharge.product_id == product.id,
                                StorageCharge.charge_date == today
                            )
                        )
                        existing = existing_result.scalar_one_or_none()
                        
                        if not existing:
                            charge = StorageCharge(
                                tenant_id=tenant.id,
                                charge_date=today,
                                product_id=product.id,
                                quantity=total_available,
                                rate=tariff.storage_rate,
                                amount=charge_amount
                            )
                            session.add(charge)
                            total_charges += 1
            
            await session.commit()
            return f"Created {total_charges} storage charges for {len(tenants)} tenants"
    
    return asyncio.run(run_calculation())
