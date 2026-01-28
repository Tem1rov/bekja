"""Initial schema migration

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-01-28 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    # Create ENUM types
    op.execute("CREATE TYPE order_status AS ENUM ('new', 'confirmed', 'awaiting_stock', 'picking', 'packed', 'shipped', 'delivered', 'cancelled')")
    
    # 1. Base tables (no foreign keys)
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('permissions', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    op.create_table(
        'tenants',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('inn', sa.String(length=12), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('legal_address', sa.Text(), nullable=True),
        sa.Column('storage_rate', sa.Numeric(precision=10, scale=2), server_default='0', nullable=False),
        sa.Column('processing_rate', sa.Numeric(precision=10, scale=2), server_default='0', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('inn')
    )
    
    op.create_table(
        'warehouses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 2. Second level tables
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('invitation_token', sa.String(length=255), nullable=True),
        sa.Column('invitation_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('password_reset_token', sa.String(length=255), nullable=True),
        sa.Column('password_reset_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer(), server_default='0', nullable=False),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('idx_users_tenant', 'users', ['tenant_id'])
    op.create_index('idx_users_email', 'users', ['email'])
    
    op.create_table(
        'warehouse_zones',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('zone_type', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('warehouse_id', 'name', name='uq_zone_warehouse_name')
    )
    op.create_index('idx_warehouse_zones_warehouse', 'warehouse_zones', ['warehouse_id'])
    
    op.create_table(
        'categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['parent_id'], ['categories.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'name', 'parent_id', name='uq_category_tenant_name_parent')
    )
    op.create_index('idx_categories_tenant', 'categories', ['tenant_id'])
    
    # 3. Third level tables
    op.create_table(
        'racks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('zone_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('levels', sa.Integer(), server_default='1', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['zone_id'], ['warehouse_zones.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('zone_id', 'code', name='uq_rack_zone_code')
    )
    op.create_index('idx_racks_zone', 'racks', ['zone_id'])
    
    op.create_table(
        'products',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sku', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('barcode', sa.String(length=100), nullable=True),
        sa.Column('unit', sa.String(length=20), server_default='шт', nullable=False),
        sa.Column('weight', sa.Numeric(precision=10, scale=3), nullable=True),
        sa.Column('length', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('width', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('height', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('cost_price', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
        sa.Column('min_stock_level', sa.Integer(), server_default='0', nullable=False),
        sa.Column('expiry_tracking', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('storage_requirements', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'sku', name='uq_product_tenant_sku')
    )
    op.create_index('idx_products_tenant', 'products', ['tenant_id'])
    op.create_index('idx_products_sku', 'products', ['tenant_id', 'sku'])
    op.create_index('idx_products_barcode', 'products', ['barcode'])
    op.create_index('idx_products_category', 'products', ['category_id'])
    
    op.create_table(
        'integrations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('marketplace', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('api_key_encrypted', sa.Text(), nullable=False),
        sa.Column('api_secret_encrypted', sa.Text(), nullable=True),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
        sa.Column('sync_interval', sa.Integer(), server_default='15', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_sync_status', sa.String(length=30), nullable=True),
        sa.Column('last_sync_error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_integrations_tenant', 'integrations', ['tenant_id'])
    op.create_index('idx_integrations_marketplace', 'integrations', ['marketplace'])
    
    # 4. Fourth level tables
    op.create_table(
        'cells',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rack_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('level', sa.Integer(), server_default='1', nullable=False),
        sa.Column('size', sa.String(length=10), server_default='M', nullable=False),
        sa.Column('max_weight', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['rack_id'], ['racks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('rack_id', 'code', name='uq_cell_rack_code')
    )
    op.create_index('idx_cells_rack', 'cells', ['rack_id'])
    
    op.create_table(
        'orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_number', sa.String(length=50), nullable=False),
        sa.Column('external_id', sa.String(length=100), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('status', postgresql.ENUM('new', 'confirmed', 'awaiting_stock', 'picking', 'packed', 'shipped', 'delivered', 'cancelled', name='order_status'), server_default='new', nullable=False),
        sa.Column('customer_name', sa.String(length=255), nullable=True),
        sa.Column('customer_phone', sa.String(length=20), nullable=True),
        sa.Column('customer_email', sa.String(length=255), nullable=True),
        sa.Column('delivery_address', sa.Text(), nullable=True),
        sa.Column('delivery_method', sa.String(length=100), nullable=True),
        sa.Column('total_amount', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
        sa.Column('cost_of_goods', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
        sa.Column('marketplace_fee', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
        sa.Column('shipping_cost', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
        sa.Column('storage_cost', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
        sa.Column('processing_cost', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
        sa.Column('packaging_cost', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
        sa.Column('other_costs', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
        sa.Column('margin', sa.Numeric(precision=12, scale=2), sa.Computed("total_amount - cost_of_goods - marketplace_fee - shipping_cost - storage_cost - processing_cost - packaging_cost - other_costs", persisted=True), nullable=False),
        sa.Column('has_manual_adjustments', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('picked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('shipped_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancellation_reason', sa.String(length=255), nullable=True),
        sa.Column('assigned_picker', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['assigned_picker'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'order_number', name='uq_order_tenant_number')
    )
    op.create_index('idx_orders_tenant', 'orders', ['tenant_id'])
    op.create_index('idx_orders_status', 'orders', ['status'])
    op.create_index('idx_orders_external', 'orders', ['external_id'])
    op.create_index('idx_orders_created', 'orders', ['created_at'])
    op.create_index('idx_orders_shipped', 'orders', ['shipped_at'])
    op.create_index('idx_orders_tenant_status_created', 'orders', ['tenant_id', 'status', 'created_at'])
    
    op.create_table(
        'tariffs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('tariff_type', sa.String(length=50), nullable=False),
        sa.Column('rate', sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=True),
        sa.Column('effective_from', sa.Date(), nullable=False),
        sa.Column('effective_to', sa.Date(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_tariffs_tenant', 'tariffs', ['tenant_id'])
    op.create_index('idx_tariffs_type', 'tariffs', ['tariff_type'])
    op.create_index('idx_tariffs_effective', 'tariffs', ['effective_from', 'effective_to'])
    
    # 5. Fifth level tables
    op.create_table(
        'inventory',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('cell_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.Integer(), server_default='0', nullable=False),
        sa.Column('reserved_quantity', sa.Integer(), server_default='0', nullable=False),
        sa.Column('lot_number', sa.String(length=100), nullable=True),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('received_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['cell_id'], ['cells.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'product_id', 'cell_id', name='uq_inventory_tenant_product_cell')
    )
    op.create_index('idx_inventory_cell', 'inventory', ['cell_id'])
    op.create_index('idx_inventory_product', 'inventory', ['product_id'])
    op.create_index('idx_inventory_tenant', 'inventory', ['tenant_id'])
    op.create_index('idx_inventory_expiry', 'inventory', ['expiry_date'], postgresql_where=sa.text('expiry_date IS NOT NULL'))
    op.create_index('idx_inventory_received', 'inventory', ['received_at'])
    
    op.create_table(
        'order_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('cost_price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('reserved_quantity', sa.Integer(), server_default='0', nullable=False),
        sa.Column('picked_quantity', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_id', 'product_id', name='uq_order_item_order_product')
    )
    op.create_index('idx_order_items_order', 'order_items', ['order_id'])
    op.create_index('idx_order_items_product', 'order_items', ['product_id'])
    
    op.create_table(
        'storage_charges',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('charge_date', sa.Date(), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('rate', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'charge_date', 'product_id', name='uq_storage_charge_tenant_date_product')
    )
    op.create_index('idx_storage_charges_date', 'storage_charges', ['charge_date'])
    op.create_index('idx_storage_charges_tenant', 'storage_charges', ['tenant_id'])
    
    op.create_table(
        'order_adjustments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('adjustment_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_order_adjustments_order', 'order_adjustments', ['order_id'])
    
    op.create_table(
        'sync_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('integration_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sync_type', sa.String(length=30), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('items_processed', sa.Integer(), server_default='0', nullable=False),
        sa.Column('items_created', sa.Integer(), server_default='0', nullable=False),
        sa.Column('items_updated', sa.Integer(), server_default='0', nullable=False),
        sa.Column('items_failed', sa.Integer(), server_default='0', nullable=False),
        sa.Column('error_details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['integration_id'], ['integrations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_sync_logs_integration', 'sync_logs', ['integration_id'])
    op.create_index('idx_sync_logs_started', 'sync_logs', ['started_at'])
    
    # 6. Sixth level tables
    op.create_table(
        'reservations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('inventory_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='reserved', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['inventory_id'], ['inventory.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['order_item_id'], ['order_items.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_reservations_order_item', 'reservations', ['order_item_id'])
    op.create_index('idx_reservations_inventory', 'reservations', ['inventory_id'])
    
    # Sessions table
    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('refresh_token_hash', sa.String(length=255), nullable=False),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_sessions_user', 'sessions', ['user_id'])
    op.create_index('idx_sessions_expires', 'sessions', ['expires_at'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('sessions')
    op.drop_table('reservations')
    op.drop_table('sync_logs')
    op.drop_table('order_adjustments')
    op.drop_table('storage_charges')
    op.drop_table('order_items')
    op.drop_table('inventory')
    op.drop_table('tariffs')
    op.drop_table('orders')
    op.drop_table('cells')
    op.drop_table('integrations')
    op.drop_table('products')
    op.drop_table('racks')
    op.drop_table('categories')
    op.drop_table('warehouse_zones')
    op.drop_table('users')
    op.drop_table('warehouses')
    op.drop_table('tenants')
    op.drop_table('roles')
    
    # Drop ENUM types
    op.execute("DROP TYPE IF EXISTS order_status")
