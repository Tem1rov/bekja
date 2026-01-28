"""Pytest configuration and fixtures."""

import pytest
from httpx import AsyncClient
from app.main import app


@pytest.fixture
async def client():
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_user():
    """Mock test user for authentication."""
    return {
        "email": "admin@fms.local",
        "password": "admin123"
    }


@pytest.fixture
async def auth_headers(client, test_user):
    """Get authentication headers."""
    # Note: Since we're using mock endpoints, we'll create a mock token
    # In real implementation, this would call the actual login endpoint
    response = await client.post("/api/v1/auth/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    
    # If login fails (expected with mock), return empty headers
    # Tests should handle both authenticated and unauthenticated cases
    if response.status_code == 200:
        token = response.json().get("access_token", "mock_token")
        return {"Authorization": f"Bearer {token}"}
    else:
        # Return mock token for testing with mock endpoints
        return {"Authorization": "Bearer mock_token"}
