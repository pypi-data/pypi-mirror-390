import pytest

import eap_sdk.runtime as rt


@pytest.mark.asyncio
async def test_arun_local_path(monkeypatch):
    called = {"local": False, "plugins": False, "telemetry": []}

    async def fake_local(flow_name: str, **params):
        called["local"] = True
        return {"success": True, "data": {}}

    def fake_import_plugins():
        called["plugins"] = True

    def fake_record_job(flow, runner, ok, err):
        called["telemetry"].append((flow, runner, ok, err))

    monkeypatch.delenv("MAESTRO_ADDR", raising=False)
    monkeypatch.delenv("ROBOT_ADDR", raising=False)
    monkeypatch.setattr(rt, "_run_local", fake_local)
    monkeypatch.setattr(rt, "import_plugins_from_env", lambda: fake_import_plugins())
    monkeypatch.setattr(rt, "record_job", fake_record_job)

    resp = await rt.arun("flow", runner="local", x=1)
    assert resp["success"] is True
    assert called["local"] and called["plugins"]
    assert called["telemetry"][0][1] == "local"


@pytest.mark.asyncio
async def test_arun_remote_path(monkeypatch):
    called = {"remote": False, "url": None, "telemetry": []}

    class FakeTransport:
        def __init__(self, base):
            called["url"] = base

        async def run(self, flow, params):
            called["remote"] = True
            return {"success": True}

    def fake_record_job(flow, runner, ok, err):
        called["telemetry"].append((flow, runner, ok, err))

    monkeypatch.setenv("MAESTRO_ADDR", "http://remote")
    monkeypatch.setattr(rt, "HTTPTransport", FakeTransport)
    monkeypatch.setattr(rt, "record_job", fake_record_job)

    resp = await rt.arun("flow", x=1)
    assert resp["success"] is True
    assert called["remote"] and called["url"] == "http://remote"
    assert called["telemetry"][0][1] == "remote"


def test_run_sync_delegates(monkeypatch):
    async def fake_arun(flow, runner="local", **params):
        return {"success": True, "data": params}

    monkeypatch.setattr(rt, "arun", fake_arun)
    resp = rt.run("f", runner="local", a=2)
    assert resp["data"] == {"a": 2}


def test_serve_function():
    # serve() is a placeholder that returns None
    result = rt.serve()
    assert result is None


@pytest.mark.asyncio
async def test_arun_remote_missing_base_url(monkeypatch):
    monkeypatch.delenv("MAESTRO_ADDR", raising=False)
    monkeypatch.delenv("ROBOT_ADDR", raising=False)

    resp = await rt.arun("flow", runner="remote")
    assert resp["success"] is False
    assert "MAESTRO_ADDR or ROBOT_ADDR" in resp["message"]
    assert resp["error"] == "ConfigError"
