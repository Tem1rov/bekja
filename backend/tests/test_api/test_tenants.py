"""Tenants API tests."""

import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.asyncio
async def test_list_tenants(client: AsyncClient, auth_headers):
    """Test list tenants endpoint."""
    response = await client.get("/api/v1/tenants", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "id" in data[0]
        assert "name" in data[0]
        assert "inn" in data[0]


@pytest.mark.asyncio
async def test_list_tenants_unauthorized(client: AsyncClient):
    """Test list tenants without authentication."""
    response = await client.get("/api/v1/tenants")
    # Should require authentication
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_create_tenant(client: AsyncClient, auth_headers):
    """Test create tenant endpoint."""
    response = await client.post("/api/v1/tenants", headers=auth_headers, json={
        "name": "Test Tenant",
        "inn": "1234567890",
        "email": "test@example.com",
        "phone": "+79991234567",
        "legal_address": "123 Main St, City",
        "storage_rate": 10.50,
        "processing_rate": 5.25,
        "is_active": True
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Tenant"
    assert data["inn"] == "1234567890"


@pytest.mark.asyncio
async def test_get_tenant(client: AsyncClient, auth_headers):
    """Test get tenant by ID."""
    tenant_id = str(uuid4())
    response = await client.get(f"/api/v1/tenants/{tenant_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == tenant_id


@pytest.mark.asyncio
async def test_update_tenant(client: AsyncClient, auth_headers):
    """Test update tenant endpoint."""
    tenant_id = str(uuid4())
    response = await client.put(f"/api/v1/tenants/{tenant_id}", headers=auth_headers, json={
        "name": "Updated Tenant",
        "is_active": False
    })
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == tenant_id
