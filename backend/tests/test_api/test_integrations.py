"""Integrations API tests."""

import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.asyncio
async def test_list_integrations(client: AsyncClient, auth_headers):
    """Test list integrations endpoint."""
    response = await client.get("/api/v1/integrations", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "id" in data[0]
        assert "marketplace" in data[0]
        assert "name" in data[0]


@pytest.mark.asyncio
async def test_list_integrations_unauthorized(client: AsyncClient):
    """Test list integrations without authentication."""
    response = await client.get("/api/v1/integrations")
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_create_integration(client: AsyncClient, auth_headers):
    """Test create integration endpoint."""
    response = await client.post("/api/v1/integrations", headers=auth_headers, json={
        "tenant_id": str(uuid4()),
        "marketplace": "wildberries",
        "name": "Wildberries Integration",
        "settings": {"auto_sync": True, "api_key": "test_key"},
        "sync_interval": 30,
        "is_active": True
    })
    assert response.status_code == 200
    data = response.json()
    assert data["marketplace"] == "wildberries"
    assert data["name"] == "Wildberries Integration"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_sync_integration(client: AsyncClient, auth_headers):
    """Test sync integration endpoint."""
    integration_id = str(uuid4())
    response = await client.post(
        f"/api/v1/integrations/{integration_id}/sync",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["integration_id"] == integration_id
    assert "status" in data
    assert data["status"] == "running"
    assert "sync_id" in data
    assert "started_at" in data
