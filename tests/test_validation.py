"""E2E tests for request validation and error handling."""

import pytest


@pytest.mark.asyncio
async def test_create_task_missing_title(client):
    resp = await client.post("/api/v1/tasks", json={
        "description": "No title provided",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_task_empty_title(client):
    resp = await client.post("/api/v1/tasks", json={
        "title": "",
        "description": "Empty title",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_task_invalid_priority(client):
    resp = await client.post("/api/v1/tasks", json={
        "title": "Test",
        "description": "Invalid priority",
        "priority": "urgent",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_task_title_too_long(client):
    resp = await client.post("/api/v1/tasks", json={
        "title": "x" * 501,
        "description": "Title exceeds 500 chars",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_execute_missing_query(client):
    resp = await client.post("/execute", json={})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_execute_query_too_long(client):
    resp = await client.post("/execute", json={"query": "x" * 501})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_invalid_uuid_path(client):
    resp = await client.get("/api/v1/tasks/not-a-uuid")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_tasks_limit_validation(client):
    resp = await client.get("/api/v1/tasks", params={"limit": 0})
    assert resp.status_code == 422

    resp2 = await client.get("/api/v1/tasks", params={"limit": 101})
    assert resp2.status_code == 422


@pytest.mark.asyncio
async def test_list_tasks_negative_offset(client):
    resp = await client.get("/api/v1/tasks", params={"offset": -1})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_root_serves_html(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]


@pytest.mark.asyncio
async def test_docs_endpoint(client):
    resp = await client.get("/docs")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_openapi_json(client):
    resp = await client.get("/openapi.json")
    assert resp.status_code == 200
    data = resp.json()
    assert "paths" in data
    assert "/api/v1/tasks" in data["paths"]
    assert "/execute" in data["paths"]
    assert "/health" in data["paths"]
