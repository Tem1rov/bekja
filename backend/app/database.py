"""SQLAlchemy async database engine configuration."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.config import settings
from app.models.base import Base

# Import all models to register them with Base
from app.models import (  # noqa: F401
    Tenant,
    Role,
    User,
    Session,
    Category,
    Product,
    Warehouse,
    Zone,
    Rack,
    Cell,
    Inventory,
    Receipt,
    ReceiptItem,
    Transfer,
    Order,
    OrderItem,
    Reservation,
    OrderHistory,
    Tariff,
    StorageCharge,
    OrderAdjustment,
    MarketplaceFee,
    Integration,
    SyncLog,
    Notification,
)

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:
    """Dependency for getting database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
