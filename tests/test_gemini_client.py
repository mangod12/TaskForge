import asyncio

import pytest


@pytest.mark.asyncio
async def test_get_client_singleton_under_concurrency(monkeypatch):
    from app.llm import gemini_client as gc

    created = []

    class DummyClient:
        pass

    def fake_build():
        c = DummyClient()
        created.append(c)
        return c

    gc._client = None
    gc._client_lock = None
    monkeypatch.setattr(gc, "_build_client", fake_build)

    clients = await asyncio.gather(*[gc.get_client() for _ in range(25)])
    assert len(created) == 1
    assert all(client is clients[0] for client in clients)
