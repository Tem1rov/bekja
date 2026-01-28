"""Script to seed initial data into the database."""

import asyncio
from uuid import UUID
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.config import settings
from app.database import AsyncSessionLocal


async def seed_data():
    """Seed initial data: roles, tenant, admin user, warehouse."""
    
    async with AsyncSessionLocal() as session:
        try:
            # 1. Insert roles
            print("Inserting roles...")
            await session.execute(
                text("""
                    INSERT INTO roles (id, name, permissions) VALUES
                    (1, 'admin', '{"*": true}'::jsonb),
                    (2, 'manager', '{
                        "orders:read": true, "orders:write": true,
                        "products:read": true, "products:write": true,
                        "reports:read": true, "reports:export": true,
                        "inventory:read": true
                    }'::jsonb),
                    (3, 'warehouse', '{
                        "orders:read": true, "orders:pick": true,
                        "inventory:read": true, "inventory:write": true,
                        "receipts:write": true
                    }'::jsonb),
                    (4, 'client', '{
                        "orders:read:own": true, "products:read:own": true,
                        "reports:read:own": true, "inventory:read:own": true
                    }'::jsonb)
                    ON CONFLICT (id) DO NOTHING
                """)
            )
            
            # 2. Insert default tenant
            print("Inserting default tenant...")
            default_tenant_id = UUID('00000000-0000-0000-0000-000000000001')
            await session.execute(
                text("""
                    INSERT INTO tenants (id, name, inn, email, is_active)
                    VALUES (:id, 'Default Tenant', '0000000000', 'tenant@fms.local', TRUE)
                    ON CONFLICT (inn) DO NOTHING
                """),
                {"id": str(default_tenant_id)}
            )
            
            # 3. Insert admin user
            # Password: admin123 (bcrypt hash)
            print("Inserting admin user...")
            admin_user_id = UUID('00000000-0000-0000-0000-000000000001')
            admin_password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.V.qJ/FyGJ.YJTS'
            await session.execute(
                text("""
                    INSERT INTO users (id, tenant_id, role_id, email, password_hash, full_name, is_active)
                    VALUES (:id, NULL, 1, 'admin@fms.local', :password_hash, 'System Administrator', TRUE)
                    ON CONFLICT (email) DO NOTHING
                """),
                {
                    "id": str(admin_user_id),
                    "password_hash": admin_password_hash
                }
            )
            
            # 4. Insert main warehouse
            print("Inserting main warehouse...")
            warehouse_id = UUID('00000000-0000-0000-0000-000000000001')
            result = await session.execute(
                text("SELECT COUNT(*) FROM warehouses WHERE id = :id"),
                {"id": str(warehouse_id)}
            )
            if result.scalar() == 0:
                await session.execute(
                    text("""
                        INSERT INTO warehouses (id, name, address, is_active)
                        VALUES (:id, 'Main Warehouse', 'г. Москва', TRUE)
                    """),
                    {"id": str(warehouse_id)}
                )
            else:
                print("Warehouse already exists, skipping...")
            
            await session.commit()
            print("✅ Initial data seeded successfully!")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding data: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed_data())
