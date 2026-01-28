"""Tenant service."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.models import Tenant
from .schemas import TenantCreate, TenantUpdate


class TenantService:
    """Service for tenant operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def list_tenants(self, skip: int = 0, limit: int = 100) -> list[Tenant]:
        """List active tenants."""
        result = await self.db.execute(
            select(Tenant).where(Tenant.is_active == True).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def get_tenant(self, tenant_id: UUID) -> Tenant | None:
        """Get tenant by ID."""
        return await self.db.get(Tenant, tenant_id)
    
    async def create_tenant(self, data: TenantCreate) -> Tenant:
        """Create a new tenant."""
        tenant = Tenant(**data.model_dump())
        self.db.add(tenant)
        await self.db.commit()
        await self.db.refresh(tenant)
        return tenant
    
    async def update_tenant(self, tenant_id: UUID, data: TenantUpdate) -> Tenant:
        """Update tenant."""
        tenant = await self.get_tenant(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")
        
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(tenant, key, value)
        
        await self.db.commit()
        await self.db.refresh(tenant)
        return tenant
    
    async def deactivate_tenant(self, tenant_id: UUID) -> None:
        """Deactivate tenant."""
        tenant = await self.get_tenant(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")
        
        tenant.is_active = False
        await self.db.commit()
