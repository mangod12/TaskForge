import pytest


@pytest.mark.asyncio
async def test_cors_disallows_untrusted_origin(client):
    resp = await client.options(
        "/api/v1/tasks",
        headers={
            "Origin": "https://evil.example",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert "access-control-allow-origin" not in resp.headers


@pytest.mark.asyncio
async def test_mcp_fallback_marker(monkeypatch):
    from app import mcp_client

    class _BrokenCtx:
        async def __aenter__(self):
            raise RuntimeError("mcp down")

        async def __aexit__(self, exc_type, exc, tb):
            return False

    async def fake_execute(name, args):
        return {"ok": True, "name": name}

    import mcp.client.sse
    monkeypatch.setattr(mcp.client.sse, "sse_client", lambda *_args, **_kwargs: _BrokenCtx())
    monkeypatch.setattr("app.tools.registry.tool_registry.execute", fake_execute)

    result = await mcp_client.call_tool_via_mcp("x", {"a": 1})
    assert result["ok"] is True
    assert result["_mcp_fallback"] is True
