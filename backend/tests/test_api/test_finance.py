"""Finance API tests."""

import pytest
from httpx import AsyncClient
from uuid import uuid4
from datetime import date


@pytest.mark.asyncio
async def test_list_tariffs(client: AsyncClient, auth_headers):
    """Test list tariffs endpoint."""
    response = await client.get("/api/v1/finance/tariffs", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "id" in data[0]
        assert "tariff_type" in data[0]
        assert "rate" in data[0]


@pytest.mark.asyncio
async def test_list_tariffs_unauthorized(client: AsyncClient):
    """Test list tariffs without authentication."""
    response = await client.get("/api/v1/finance/tariffs")
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_create_tariff(client: AsyncClient, auth_headers):
    """Test create tariff endpoint."""
    response = await client.post("/api/v1/finance/tariffs", headers=auth_headers, json={
        "tenant_id": str(uuid4()),
        "tariff_type": "storage",
        "rate": 10.50,
        "unit": "m³/day",
        "effective_from": "2025-01-01",
        "effective_to": None
    })
    assert response.status_code == 200
    data = response.json()
    assert data["tariff_type"] == "storage"
    assert float(data["rate"]) == 10.50


@pytest.mark.asyncio
async def test_get_order_pnl(client: AsyncClient, auth_headers):
    """Test get order PnL endpoint."""
    order_id = str(uuid4())
    response = await client.get(f"/api/v1/finance/orders/{order_id}/pnl", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == order_id
    assert "total_amount" in data
    assert "cost_of_goods" in data
    assert "margin" in data
    assert "margin_percent" in data


@pytest.mark.asyncio
async def test_get_pnl_report(client: AsyncClient, auth_headers):
    """Test get PnL report endpoint."""
    start_date = "2024-01-01"
    end_date = "2024-12-31"
    
    response = await client.get(
        f"/api/v1/finance/reports/pnl?start_date={start_date}&end_date={end_date}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "period_start" in data
    assert "period_end" in data
    assert "total_revenue" in data
    assert "total_margin" in data
    assert "margin_percent" in data
    assert "orders" in data
