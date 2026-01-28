"""Warehouse API tests."""

import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.asyncio
async def test_list_warehouses(client: AsyncClient, auth_headers):
    """Test list warehouses endpoint."""
    response = await client.get("/api/v1/warehouses", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "id" in data[0]
        assert "name" in data[0]
        assert "address" in data[0]


@pytest.mark.asyncio
async def test_list_warehouses_unauthorized(client: AsyncClient):
    """Test list warehouses without authentication."""
    response = await client.get("/api/v1/warehouses")
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_list_zones(client: AsyncClient, auth_headers):
    """Test list zones endpoint."""
    warehouse_id = str(uuid4())
    response = await client.get(f"/api/v1/warehouses/{warehouse_id}/zones", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "id" in data[0]
        assert "warehouse_id" in data[0]
        assert "name" in data[0]


@pytest.mark.asyncio
async def test_create_zone(client: AsyncClient, auth_headers):
    """Test create zone endpoint."""
    warehouse_id = str(uuid4())
    response = await client.post(
        f"/api/v1/warehouses/{warehouse_id}/zones",
        headers=auth_headers,
        json={
            "name": "Zone C",
            "zone_type": "storage",
            "is_active": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["warehouse_id"] == warehouse_id
    assert data["name"] == "Zone C"


@pytest.mark.asyncio
async def test_list_cells(client: AsyncClient, auth_headers):
    """Test list cells endpoint."""
    response = await client.get("/api/v1/warehouses/cells", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "id" in data[0]
        assert "code" in data[0]


@pytest.mark.asyncio
async def test_list_inventory(client: AsyncClient, auth_headers):
    """Test list inventory endpoint."""
    response = await client.get("/api/v1/warehouses/inventory", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "id" in data[0]
        assert "product_id" in data[0]
        assert "quantity" in data[0]


@pytest.mark.asyncio
async def test_create_receipt(client: AsyncClient, auth_headers):
    """Test create receipt endpoint."""
    response = await client.post("/api/v1/warehouses/receipts", headers=auth_headers, json={
        "warehouse_id": str(uuid4()),
        "tenant_id": str(uuid4()),
        "items": [
            {
                "product_id": str(uuid4()),
                "quantity": 10,
                "cell_id": str(uuid4()),
                "lot_number": "LOT-001"
            }
        ]
    })
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "status" in data
    assert data["status"] == "created"


@pytest.mark.asyncio
async def test_create_transfer(client: AsyncClient, auth_headers):
    """Test create transfer endpoint."""
    response = await client.post("/api/v1/warehouses/transfers", headers=auth_headers, json={
        "from_cell_id": str(uuid4()),
        "to_cell_id": str(uuid4()),
        "product_id": str(uuid4()),
        "quantity": 5
    })
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "status" in data
    assert data["status"] == "created"
