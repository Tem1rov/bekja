"""Orders API tests."""

import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.asyncio
async def test_list_orders(client: AsyncClient, auth_headers):
    """Test list orders endpoint."""
    response = await client.get("/api/v1/orders", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "id" in data[0]
        assert "order_number" in data[0]
        assert "status" in data[0]


@pytest.mark.asyncio
async def test_list_orders_unauthorized(client: AsyncClient):
    """Test list orders without authentication."""
    response = await client.get("/api/v1/orders")
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_create_order(client: AsyncClient, auth_headers):
    """Test create order endpoint."""
    response = await client.post("/api/v1/orders", headers=auth_headers, json={
        "tenant_id": str(uuid4()),
        "order_number": "ORD-TEST-001",
        "external_id": "EXT-001",
        "source": "manual",
        "customer_name": "Test Customer",
        "customer_phone": "+79001234567",
        "customer_email": "customer@example.com",
        "delivery_address": "Test Address",
        "delivery_method": "courier",
        "items": [
            {
                "product_id": str(uuid4()),
                "quantity": 2,
                "price": 1000
            }
        ],
        "notes": "Test order"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["order_number"] is not None
    assert data["status"] == "new"


@pytest.mark.asyncio
async def test_get_order(client: AsyncClient, auth_headers):
    """Test get order by ID."""
    order_id = str(uuid4())
    response = await client.get(f"/api/v1/orders/{order_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id


@pytest.mark.asyncio
async def test_update_order(client: AsyncClient, auth_headers):
    """Test update order endpoint."""
    order_id = str(uuid4())
    response = await client.put(f"/api/v1/orders/{order_id}", headers=auth_headers, json={
        "status": "confirmed",
        "customer_name": "Updated Customer"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id


@pytest.mark.asyncio
async def test_reserve_order(client: AsyncClient, auth_headers):
    """Test reserve order endpoint."""
    order_id = str(uuid4())
    response = await client.post(f"/api/v1/orders/{order_id}/reserve", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == order_id
    assert "status" in data


@pytest.mark.asyncio
async def test_ship_order(client: AsyncClient, auth_headers):
    """Test ship order endpoint."""
    order_id = str(uuid4())
    response = await client.post(f"/api/v1/orders/{order_id}/ship", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == order_id
    assert data["status"] == "shipped"
    assert "tracking_number" in data
