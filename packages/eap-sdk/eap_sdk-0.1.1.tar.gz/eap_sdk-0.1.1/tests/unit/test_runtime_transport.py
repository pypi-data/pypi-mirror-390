import pytest

from eap_sdk import RunContext, register_hook
from eap_sdk.runtime import _HOOKS, HTTPTransport, LocalTransport


@pytest.mark.asyncio
async def test_local_transport_delegates(monkeypatch):
    called = {}

    async def fake_run_local(flow_name: str, **params):
        called["args"] = (flow_name, params)
        return {"success": True, "data": {}}

    import eap_sdk.runtime as rt

    monkeypatch.setattr(rt, "_run_local", fake_run_local)
    lt = LocalTransport()
    resp = await lt.run("f", {"x": 1})
    assert resp["success"] is True
    assert called["args"][0] == "f"
    assert called["args"][1] == {"x": 1}


@pytest.mark.asyncio
async def test_http_transport_success(monkeypatch):
    class FakeResponse:
        def __init__(self, json_obj):
            self._json = json_obj

        def raise_for_status(self):
            return None

        def json(self):
            return self._json

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, json):
            return FakeResponse({"success": True, "data": {"ok": 1}})

    import httpx

    monkeypatch.setattr(httpx, "AsyncClient", lambda timeout: FakeClient())

    t = HTTPTransport("https://host")
    resp = await t.run("flow", {"a": 1})
    assert resp["success"] is True and resp["data"] == {"ok": 1}


@pytest.mark.asyncio
async def test_http_transport_http_error(monkeypatch):
    class FakeHTTPError(Exception):
        pass

    class FakeResponse:
        def raise_for_status(self):
            raise FakeHTTPError("boom")

        def json(self):
            return {}

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, json):
            return FakeResponse()

    import httpx

    monkeypatch.setattr(httpx, "AsyncClient", lambda timeout: FakeClient())
    monkeypatch.setattr(httpx, "HTTPError", FakeHTTPError)

    t = HTTPTransport("https://host")
    resp = await t.run("flow", {"a": 1})
    assert resp["success"] is False
    assert resp["message"] == "HTTP error"
    assert "boom" in resp["error"]


@pytest.fixture(autouse=True)
def clear_hooks():
    """Clear hooks before and after each test."""
    _HOOKS["pre"].clear()
    _HOOKS["post"].clear()
    yield
    _HOOKS["pre"].clear()
    _HOOKS["post"].clear()


@pytest.mark.asyncio
async def test_http_transport_pre_hook_failure(monkeypatch):
    """Test HTTPTransport stops execution when pre-hook fails."""
    hook_called = []

    async def failing_pre_hook(ctx: RunContext, flow_name: str, params: dict) -> None:
        hook_called.append("called")
        raise RuntimeError("Pre-hook failed")

    register_hook("pre", failing_pre_hook)

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, json):
            hook_called.append("http_called")  # Should not be called
            return None

    import httpx

    monkeypatch.setattr(httpx, "AsyncClient", lambda timeout: FakeClient())

    t = HTTPTransport("https://host")
    resp = await t.run("flow", {"a": 1})
    assert resp["success"] is False
    assert "Pre-execution hook failed" in resp["message"]
    assert hook_called == ["called"]  # HTTP should not be called


@pytest.mark.asyncio
async def test_http_transport_post_hook_error_handling(monkeypatch):
    """Test HTTPTransport handles post-hook errors gracefully."""
    hook_called = []

    async def failing_post_hook(ctx: RunContext, result: dict) -> None:
        hook_called.append("called")
        raise RuntimeError("Post-hook error")

    register_hook("post", failing_post_hook)

    class FakeResponse:
        def __init__(self, json_obj):
            self._json = json_obj

        def raise_for_status(self):
            return None

        def json(self):
            return self._json

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, json):
            return FakeResponse({"success": True, "data": {"ok": 1}})

    import httpx

    monkeypatch.setattr(httpx, "AsyncClient", lambda timeout: FakeClient())

    t = HTTPTransport("https://host")
    resp = await t.run("flow", {"a": 1})
    # Execution should succeed despite post-hook error
    assert resp["success"] is True
    assert hook_called == ["called"]


@pytest.mark.asyncio
async def test_http_transport_outer_exception_handler(monkeypatch):
    """Test HTTPTransport handles exceptions outside HTTP call."""
    hook_called = []

    async def post_hook(ctx: RunContext, result: dict) -> None:
        hook_called.append("called")

    register_hook("post", post_hook)

    class FakeClient:
        async def __aenter__(self):
            raise RuntimeError("Client initialization failed")

        async def __aexit__(self, exc_type, exc, tb):
            return False

    import httpx

    monkeypatch.setattr(httpx, "AsyncClient", lambda timeout: FakeClient())

    t = HTTPTransport("https://host")
    resp = await t.run("flow", {"a": 1})
    assert resp["success"] is False
    assert resp["message"] == "Transport error"
    assert hook_called == ["called"]  # Post-hook should still be called


@pytest.mark.asyncio
async def test_http_transport_post_hook_exception_in_error_path(monkeypatch):
    """Test HTTPTransport handles post-hook exceptions in error path."""
    hook_called = []

    async def failing_post_hook(ctx: RunContext, result: dict) -> None:
        hook_called.append("called")
        raise RuntimeError("Post-hook error")

    register_hook("post", failing_post_hook)

    class FakeClient:
        async def __aenter__(self):
            raise RuntimeError("Client initialization failed")

        async def __aexit__(self, exc_type, exc, tb):
            return False

    import httpx

    monkeypatch.setattr(httpx, "AsyncClient", lambda timeout: FakeClient())

    t = HTTPTransport("https://host")
    resp = await t.run("flow", {"a": 1})
    # Execution should fail, but post-hook exception should be ignored
    assert resp["success"] is False
    assert resp["message"] == "Transport error"
    assert hook_called == ["called"]  # Post-hook should be called
