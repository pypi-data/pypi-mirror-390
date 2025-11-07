"""Tests for entrypoint inference and lookup."""

import pytest

from eap_sdk import decorators


@pytest.fixture(autouse=True)
def clear_registry():
    decorators._FLOWS.clear()
    yield
    decorators._FLOWS.clear()


def test_entrypoint_inference():
    """Test that entrypoint is inferred and stored correctly."""

    @decorators.flow("my_flow")
    async def my_flow(ctx):
        return {"ok": True}

    assert hasattr(my_flow, "_eap_flow_entry")
    entrypoint = my_flow._eap_flow_entry
    assert ":" in entrypoint
    assert entrypoint.endswith(":my_flow")


def test_entrypoint_lookup():
    """Test that flows can be looked up by entrypoint."""

    @decorators.flow("test_flow")
    async def test_flow(ctx):
        return {"result": "test"}

    entrypoint = test_flow._eap_flow_entry

    # Lookup by name still works
    fn1 = decorators.get_flow("test_flow")
    assert fn1 is test_flow

    # Lookup by entrypoint also works
    fn2 = decorators.get_flow(entrypoint)
    assert fn2 is test_flow


def test_entrypoint_fallback():
    """Test entrypoint inference fallback for __main__."""

    # Create a function without a module context
    @decorators.flow("fallback_flow")
    async def fallback_flow(ctx):
        return {}

    entrypoint = fallback_flow._eap_flow_entry
    assert isinstance(entrypoint, str)
    assert ":" in entrypoint
