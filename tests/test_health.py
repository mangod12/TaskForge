"""E2E tests for the health check endpoint."""

import pytest


@pytest.mark.asyncio
async def test_health_returns_200(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("healthy", "degraded")
    assert "database" in data
    assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_health_db_connected(client):
    resp = await client.get("/health")
    data = resp.json()
    assert data["database"] == "connected"
    assert data["status"] == "healthy"
