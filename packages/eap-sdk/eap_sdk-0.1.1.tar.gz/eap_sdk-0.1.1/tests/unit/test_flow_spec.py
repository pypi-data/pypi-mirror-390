"""Tests for flow specification generation."""

import pytest

from eap_sdk import decorators, runtime


@pytest.fixture(autouse=True)
def clear_registry():
    decorators._FLOWS.clear()
    yield
    decorators._FLOWS.clear()


def test_build_flow_spec():
    """Test that build_flow_spec generates correct structure."""

    @decorators.flow("my_flow")
    async def my_flow(ctx):
        return {}

    spec = runtime.build_flow_spec(my_flow, "my_flow")

    assert spec["flow_id"] == "py.my_flow"
    assert spec["version"] == 1
    assert isinstance(spec["tasks"], list)
    assert len(spec["tasks"]) == 1
    assert spec["tasks"][0]["id"] == "task-1"
    assert spec["tasks"][0]["name"] == "my_flow"
    assert "entrypoint" in spec["tasks"][0]


def test_build_flow_spec_uses_entrypoint():
    """Test that build_flow_spec uses stored entrypoint."""

    @decorators.flow("test_flow")
    async def test_flow(ctx):
        return {}

    entrypoint = test_flow._eap_flow_entry
    spec = runtime.build_flow_spec(test_flow, "test_flow")

    assert spec["tasks"][0]["entrypoint"] == entrypoint


def test_build_flow_spec_infers_entrypoint_if_missing():
    """Test that build_flow_spec infers entrypoint if not stored."""

    async def standalone_flow(ctx):
        return {}

    # Remove entrypoint attribute if it exists
    if hasattr(standalone_flow, "_eap_flow_entry"):
        delattr(standalone_flow, "_eap_flow_entry")

    spec = runtime.build_flow_spec(standalone_flow, "standalone_flow")

    assert "entrypoint" in spec["tasks"][0]
    assert ":" in spec["tasks"][0]["entrypoint"]
