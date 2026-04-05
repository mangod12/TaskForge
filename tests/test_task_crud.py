"""E2E tests for task CRUD endpoints."""

import uuid

import pytest


@pytest.mark.asyncio
async def test_create_task_returns_202(client):
    resp = await client.post("/api/v1/tasks", json={
        "title": "Flood in Odisha",
        "description": "7.2 earthquake hit Region-7. Assess damage.",
        "priority": "high",
    })
    assert resp.status_code == 202
    data = resp.json()
    assert "task_id" in data
    assert data["status"] == "pending"
    uuid.UUID(data["task_id"])  # validates UUID format


@pytest.mark.asyncio
async def test_create_task_default_priority(client):
    resp = await client.post("/api/v1/tasks", json={
        "title": "Supply shortage",
        "description": "300 food units needed",
    })
    assert resp.status_code == 202


@pytest.mark.asyncio
async def test_list_tasks_empty(client):
    resp = await client.get("/api/v1/tasks")
    assert resp.status_code == 200
    data = resp.json()
    assert data["tasks"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_tasks_after_create(client):
    await client.post("/api/v1/tasks", json={
        "title": "Test task 1",
        "description": "Desc 1",
    })
    await client.post("/api/v1/tasks", json={
        "title": "Test task 2",
        "description": "Desc 2",
    })
    resp = await client.get("/api/v1/tasks")
    data = resp.json()
    assert data["total"] >= 2
    titles = [t["title"] for t in data["tasks"]]
    assert "Test task 1" in titles
    assert "Test task 2" in titles


@pytest.mark.asyncio
async def test_list_tasks_pagination(client):
    for i in range(5):
        await client.post("/api/v1/tasks", json={
            "title": f"Paginated task {i}",
            "description": f"Desc {i}",
        })
    resp = await client.get("/api/v1/tasks", params={"limit": 2, "offset": 0})
    data = resp.json()
    assert len(data["tasks"]) == 2

    resp2 = await client.get("/api/v1/tasks", params={"limit": 2, "offset": 2})
    data2 = resp2.json()
    assert len(data2["tasks"]) == 2

    # No overlap between pages
    ids_page1 = {t["id"] for t in data["tasks"]}
    ids_page2 = {t["id"] for t in data2["tasks"]}
    assert ids_page1.isdisjoint(ids_page2)


@pytest.mark.asyncio
async def test_get_task_by_id(client):
    create_resp = await client.post("/api/v1/tasks", json={
        "title": "Get me by ID",
        "description": "Testing GET by ID",
        "priority": "critical",
    })
    task_id = create_resp.json()["task_id"]

    resp = await client.get(f"/api/v1/tasks/{task_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == task_id
    assert data["title"] == "Get me by ID"
    assert data["priority"] == "critical"
    # Background pipeline may complete before GET (runs inline in ASGI transport)
    assert data["status"] in ("pending", "completed", "failed")
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_get_task_not_found(client):
    fake_id = uuid.uuid4()
    resp = await client.get(f"/api/v1/tasks/{fake_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_task(client):
    create_resp = await client.post("/api/v1/tasks", json={
        "title": "Delete me",
        "description": "About to be deleted",
    })
    task_id = create_resp.json()["task_id"]

    del_resp = await client.delete(f"/api/v1/tasks/{task_id}")
    assert del_resp.status_code == 200

    get_resp = await client.get(f"/api/v1/tasks/{task_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_task_not_found(client):
    fake_id = uuid.uuid4()
    resp = await client.delete(f"/api/v1/tasks/{fake_id}")
    assert resp.status_code == 404
