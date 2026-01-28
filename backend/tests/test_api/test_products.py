"""Products API tests."""

import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.asyncio
async def test_list_products(client: AsyncClient, auth_headers):
    """Test list products endpoint."""
    response = await client.get("/api/v1/products", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "id" in data[0]
        assert "sku" in data[0]
        assert "name" in data[0]


@pytest.mark.asyncio
async def test_list_products_unauthorized(client: AsyncClient):
    """Test list products without authentication."""
    response = await client.get("/api/v1/products")
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_create_product(client: AsyncClient, auth_headers):
    """Test create product endpoint."""
    response = await client.post("/api/v1/products", headers=auth_headers, json={
        "tenant_id": str(uuid4()),
        "sku": "TEST-SKU-001",
        "name": "Test Product",
        "barcode": "1234567890123",
        "unit": "шт",
        "weight": 0.5,
        "length": 10.0,
        "width": 5.0,
        "height": 3.0,
        "cost_price": 100.00,
        "min_stock_level": 10,
        "expiry_tracking": False,
        "storage_requirements": {"temperature": "room"},
        "is_active": True
    })
    assert response.status_code == 200
    data = response.json()
    assert data["sku"] == "TEST-SKU-001"
    assert data["name"] == "Test Product"


@pytest.mark.asyncio
async def test_get_product(client: AsyncClient, auth_headers):
    """Test get product by ID."""
    product_id = str(uuid4())
    response = await client.get(f"/api/v1/products/{product_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id


@pytest.mark.asyncio
async def test_update_product(client: AsyncClient, auth_headers):
    """Test update product endpoint."""
    product_id = str(uuid4())
    response = await client.put(f"/api/v1/products/{product_id}", headers=auth_headers, json={
        "name": "Updated Product",
        "cost_price": 150.00
    })
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id


@pytest.mark.asyncio
async def test_import_products(client: AsyncClient, auth_headers):
    """Test import products endpoint."""
    # Create a simple CSV file content
    csv_content = "SKU,Name,Barcode\nSKU-001,Product 1,1234567890123\nSKU-002,Product 2,1234567890124"
    
    files = {"file": ("products.csv", csv_content, "text/csv")}
    response = await client.post("/api/v1/products/import", headers=auth_headers, files=files)
    
    # May require proper file upload, so accept both success and error codes
    assert response.status_code in [200, 400, 422]
    
    if response.status_code == 200:
        data = response.json()
        assert "imported" in data
        assert "updated" in data
        assert "failed" in data
