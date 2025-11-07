import asyncio

import pytest

from eap_sdk import decorators


@pytest.fixture(autouse=True)
def clear_registry():
    decorators._FLOWS.clear()
    yield
    decorators._FLOWS.clear()


def test_flow_registers_and_get_flow():
    @decorators.flow()
    async def foo(ctx):
        return {"ok": True}

    fn = decorators.get_flow("foo")
    assert asyncio.iscoroutinefunction(fn)


def test_flow_duplicate_registration_error():
    @decorators.flow("same")
    async def f1(ctx):
        return {}

    with pytest.raises(ValueError):

        @decorators.flow("same")
        async def f2(ctx):
            return {}


def test_flow_non_async_rejected():
    with pytest.raises(TypeError):

        @decorators.flow()
        def not_async(ctx):
            return {}


def test_get_flow_unknown():
    with pytest.raises(KeyError):
        decorators.get_flow("unknown")


def test_flow_stores_entrypoint():
    """Test that flow decorator stores entrypoint attribute."""

    @decorators.flow("entrypoint_test")
    async def entrypoint_test(ctx):
        return {}

    assert hasattr(entrypoint_test, "_eap_flow_entry")
    entrypoint = entrypoint_test._eap_flow_entry
    assert isinstance(entrypoint, str)
    assert ":" in entrypoint
