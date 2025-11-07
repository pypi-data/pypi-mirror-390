"""Tests for .serve() method on flows."""

import pytest

from eap_sdk import decorators, runtime


@pytest.fixture(autouse=True)
def clear_registry():
    decorators._FLOWS.clear()
    yield
    decorators._FLOWS.clear()


def test_serve_method_attached():
    """Test that .serve() method is attached to flow functions."""

    @decorators.flow("test_flow")
    async def test_flow(ctx):
        return {"ok": True}

    assert hasattr(test_flow, "serve")
    assert callable(test_flow.serve)


def test_serve_requires_maestro_http(monkeypatch):
    """Test that .serve() requires MAESTRO_HTTP environment variable."""

    @decorators.flow("test_flow")
    async def test_flow(ctx):
        return {"ok": True}

    monkeypatch.delenv("MAESTRO_HTTP", raising=False)

    with pytest.raises(RuntimeError, match="MAESTRO_HTTP"):
        test_flow.serve(pool="dev", params={"x": 1})


def test_serve_calls_submit_remote_http(monkeypatch):
    """Test that .serve() calls submit_remote_http with correct arguments."""
    called = {"spec": None, "deployment": None, "params": None}

    def mock_submit(base, spec, deployment, params):
        called["spec"] = spec
        called["deployment"] = deployment
        called["params"] = params
        return "run-123"

    monkeypatch.setenv("MAESTRO_HTTP", "http://localhost:8080")
    monkeypatch.setattr(runtime, "submit_remote_http", mock_submit)

    @decorators.flow("my_flow")
    async def my_flow(ctx):
        return {}

    run_id = my_flow.serve(pool="prod", schedule="0 9 * * *", params={"x": 1})

    assert run_id == "run-123"
    assert called["spec"] is not None
    assert called["spec"]["flow_id"] == "py.my_flow"
    assert called["deployment"]["pool"] == "prod"
    assert called["deployment"]["schedule"] == "0 9 * * *"
    assert called["params"] == {"x": 1}


def test_serve_builds_flow_spec(monkeypatch):
    """Test that .serve() builds correct flow spec."""

    def mock_submit(base, spec, deployment, params):
        return "run-123"

    monkeypatch.setenv("MAESTRO_HTTP", "http://localhost:8080")
    monkeypatch.setattr(runtime, "submit_remote_http", mock_submit)

    @decorators.flow("test_flow")
    async def test_flow(ctx):
        return {}

    run_id = test_flow.serve(pool="dev")

    assert run_id == "run-123"
    # Verify spec structure by checking mock was called
    # (Actual spec structure tested in flow_spec tests)
