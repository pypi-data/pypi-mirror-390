"""Tests for submit_remote_http function."""

import pytest

from eap_sdk.runtime import submit_remote_http


def test_submit_remote_http_success(monkeypatch):
    """Test successful submission to remote HTTP endpoint."""

    class FakeResponse:
        def __init__(self, json_obj):
            self._json = json_obj

        def raise_for_status(self):
            return None

        def json(self):
            return self._json

    def mock_post(url, json, timeout):
        assert url == "https://maestro.example.com/run"
        assert json["spec"]["flow_id"] == "py.test_flow"
        assert json["deployment"]["pool"] == "prod"
        assert json["params"] == {"x": 1}
        return FakeResponse({"success": True, "run_id": "run-123"})

    import httpx

    monkeypatch.setattr(httpx, "post", mock_post)

    flow_spec = {"flow_id": "py.test_flow", "version": 1, "tasks": []}
    deployment = {"pool": "prod"}
    params = {"x": 1}

    run_id = submit_remote_http("https://maestro.example.com", flow_spec, deployment, params)
    assert run_id == "run-123"


def test_submit_remote_http_strips_trailing_slash(monkeypatch):
    """Test that base URL trailing slash is stripped."""
    called_url = None

    def mock_post(url, json, timeout):
        nonlocal called_url
        called_url = url
        return type(
            "Response",
            (),
            {
                "raise_for_status": lambda self: None,
                "json": lambda self: {"success": True, "run_id": "run-123"},
            },
        )()

    import httpx

    monkeypatch.setattr(httpx, "post", mock_post)

    submit_remote_http("https://maestro.example.com/", {}, {}, {})
    assert called_url == "https://maestro.example.com/run"


def test_submit_remote_http_http_error(monkeypatch):
    """Test that HTTP errors are raised."""

    class FakeHTTPError(Exception):
        pass

    def mock_post(url, json, timeout):
        raise FakeHTTPError("Connection failed")

    import httpx

    monkeypatch.setattr(httpx, "post", mock_post)
    monkeypatch.setattr(httpx, "HTTPError", FakeHTTPError)

    with pytest.raises(FakeHTTPError, match="Connection failed"):
        submit_remote_http("https://maestro.example.com", {}, {}, {})


def test_submit_remote_http_failure_response(monkeypatch):
    """Test that non-success responses raise RuntimeError."""

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"success": False, "error": "Flow not found"}

    def mock_post(url, json, timeout):
        return FakeResponse()

    import httpx

    monkeypatch.setattr(httpx, "post", mock_post)

    with pytest.raises(RuntimeError, match="Remote run failed"):
        submit_remote_http("https://maestro.example.com", {}, {}, {})


def test_submit_remote_http_missing_run_id(monkeypatch):
    """Test that missing run_id raises RuntimeError."""

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"success": True}  # Missing run_id

    def mock_post(url, json, timeout):
        return FakeResponse()

    import httpx

    monkeypatch.setattr(httpx, "post", mock_post)

    with pytest.raises(RuntimeError, match="Response missing run_id"):
        submit_remote_http("https://maestro.example.com", {}, {}, {})
