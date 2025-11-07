import pytest

from eap_sdk import RunContext, clear_hooks, decorators, register_hook
from eap_sdk.plugins import _SERVICE_FACTORIES
from eap_sdk.runtime import _HOOKS, _run_local


@pytest.fixture(autouse=True)
def clear_registry():
    decorators._FLOWS.clear()
    _SERVICE_FACTORIES.clear()
    _HOOKS["pre"].clear()
    _HOOKS["post"].clear()
    yield
    decorators._FLOWS.clear()
    _SERVICE_FACTORIES.clear()
    _HOOKS["pre"].clear()
    _HOOKS["post"].clear()


@pytest.mark.asyncio
async def test_run_local_happy_path_normalization(monkeypatch):
    @decorators.flow("as_dict")
    async def f1(ctx):
        return {"a": 1}

    r1 = await _run_local("as_dict")
    assert r1["success"] is True
    assert r1["data"] == {"a": 1}

    @decorators.flow("non_dict")
    async def f2(ctx):
        return 42

    r2 = await _run_local("non_dict")
    assert r2["success"] is True
    assert r2["data"] == {"result": 42}


@pytest.mark.asyncio
async def test_run_local_unknown_flow():
    r = await _run_local("missing")
    assert r["success"] is False
    assert "Unknown flow" in r["message"] or "Unknown" in r["error"]


@pytest.mark.asyncio
async def test_run_local_exception_branches(monkeypatch):
    @decorators.flow("boom")
    async def f(ctx):
        raise RuntimeError("bad")

    # no debug: error is str(e)
    monkeypatch.delenv("EAP_DEBUG", raising=False)
    r = await _run_local("boom")
    assert r["success"] is False
    assert r["error"] == "bad"

    # debug branch includes traceback
    monkeypatch.setenv("EAP_DEBUG", "1")
    r2 = await _run_local("boom")
    assert r2["success"] is False
    assert "Traceback" in r2["error"]


# Hook tests
@pytest.mark.asyncio
async def test_pre_hook_successful_flow():
    """Test pre-hook executes before flow and can modify context."""
    hook_called = []

    async def pre_hook(ctx: RunContext, flow_name: str, params: dict) -> None:
        hook_called.append(("pre", flow_name, params))
        ctx.set("hook_data", "pre_set")

    @decorators.flow("test_flow")
    async def f(ctx: RunContext):
        assert ctx.get("hook_data") == "pre_set"
        return {"success": True}

    register_hook("pre", pre_hook)
    result = await _run_local("test_flow")
    assert result["success"] is True
    assert hook_called == [("pre", "test_flow", {})]


@pytest.mark.asyncio
async def test_pre_hook_failure_stops_execution():
    """Test pre-hook exception stops flow execution."""
    hook_called = []

    async def pre_hook(ctx: RunContext, flow_name: str, params: dict) -> None:
        hook_called.append("called")
        raise RuntimeError("Pre-hook failed")

    @decorators.flow("test_flow")
    async def f(ctx: RunContext):
        hook_called.append("flow_executed")  # Should not be called
        return {"success": True}

    register_hook("pre", pre_hook)
    result = await _run_local("test_flow")
    assert result["success"] is False
    assert "Pre-execution hook failed" in result["message"]
    assert hook_called == ["called"]  # Flow should not execute


@pytest.mark.asyncio
async def test_post_hook_on_success():
    """Test post-hook executes after successful flow execution."""
    hook_called = []

    async def post_hook(ctx: RunContext, result: dict) -> None:
        hook_called.append(("post", result["success"]))

    @decorators.flow("test_flow")
    async def f(ctx: RunContext):
        return {"success": True, "data": "test"}

    register_hook("post", post_hook)
    result = await _run_local("test_flow")
    assert result["success"] is True
    assert hook_called == [("post", True)]


@pytest.mark.asyncio
async def test_post_hook_on_failure():
    """Test post-hook executes even when flow fails."""
    hook_called = []

    async def post_hook(ctx: RunContext, result: dict) -> None:
        hook_called.append(("post", result["success"]))

    @decorators.flow("test_flow")
    async def f(ctx: RunContext):
        raise RuntimeError("Flow failed")

    register_hook("post", post_hook)
    result = await _run_local("test_flow")
    assert result["success"] is False
    assert hook_called == [("post", False)]  # Post-hook still called


@pytest.mark.asyncio
async def test_multiple_hooks_execution_order():
    """Test multiple hooks execute in registration order."""
    execution_order = []

    async def pre_hook1(ctx: RunContext, flow_name: str, params: dict) -> None:
        execution_order.append("pre1")

    async def pre_hook2(ctx: RunContext, flow_name: str, params: dict) -> None:
        execution_order.append("pre2")

    async def post_hook1(ctx: RunContext, result: dict) -> None:
        execution_order.append("post1")

    async def post_hook2(ctx: RunContext, result: dict) -> None:
        execution_order.append("post2")

    @decorators.flow("test_flow")
    async def f(ctx: RunContext):
        execution_order.append("flow")
        return {"success": True}

    register_hook("pre", pre_hook1)
    register_hook("pre", pre_hook2)
    register_hook("post", post_hook1)
    register_hook("post", post_hook2)

    result = await _run_local("test_flow")
    assert result["success"] is True
    assert execution_order == ["pre1", "pre2", "flow", "post1", "post2"]


@pytest.mark.asyncio
async def test_post_hook_error_does_not_fail_execution():
    """Test post-hook errors are logged but don't fail execution."""
    hook_called = []

    async def post_hook(ctx: RunContext, result: dict) -> None:
        hook_called.append("called")
        raise RuntimeError("Post-hook error")

    @decorators.flow("test_flow")
    async def f(ctx: RunContext):
        return {"success": True}

    register_hook("post", post_hook)
    result = await _run_local("test_flow")
    # Execution should succeed despite post-hook error
    assert result["success"] is True
    assert hook_called == ["called"]


@pytest.mark.asyncio
async def test_cleanup_registry():
    """Test cleanup functions are called in reverse order."""
    cleanup_order = []

    async def cleanup1():
        cleanup_order.append("cleanup1")

    async def cleanup2():
        cleanup_order.append("cleanup2")

    async def pre_hook(ctx: RunContext, flow_name: str, params: dict) -> None:
        ctx.register_cleanup(cleanup1)
        ctx.register_cleanup(cleanup2)

    @decorators.flow("test_flow")
    async def f(ctx: RunContext):
        return {"success": True}

    register_hook("pre", pre_hook)
    result = await _run_local("test_flow")
    assert result["success"] is True
    # Cleanup should be called in reverse order (LIFO)
    assert cleanup_order == ["cleanup2", "cleanup1"]


@pytest.mark.asyncio
async def test_cleanup_on_error():
    """Test cleanup functions are called even when flow fails."""
    cleanup_called = []

    async def cleanup():
        cleanup_called.append("called")

    async def pre_hook(ctx: RunContext, flow_name: str, params: dict) -> None:
        ctx.register_cleanup(cleanup)

    @decorators.flow("test_flow")
    async def f(ctx: RunContext):
        raise RuntimeError("Flow failed")

    register_hook("pre", pre_hook)
    result = await _run_local("test_flow")
    assert result["success"] is False
    assert cleanup_called == ["called"]  # Cleanup should still be called


@pytest.mark.asyncio
async def test_cleanup_error_does_not_fail():
    """Test cleanup errors are logged but don't fail execution."""
    cleanup_called = []

    async def cleanup():
        cleanup_called.append("called")
        raise RuntimeError("Cleanup error")

    async def pre_hook(ctx: RunContext, flow_name: str, params: dict) -> None:
        ctx.register_cleanup(cleanup)

    @decorators.flow("test_flow")
    async def f(ctx: RunContext):
        return {"success": True}

    register_hook("pre", pre_hook)
    result = await _run_local("test_flow")
    assert result["success"] is True
    assert cleanup_called == ["called"]


@pytest.mark.asyncio
async def test_clear_hooks():
    """Test clear_hooks removes registered hooks."""
    hook_called = []

    async def pre_hook(ctx: RunContext, flow_name: str, params: dict) -> None:
        hook_called.append("called")

    @decorators.flow("test_flow")
    async def f(ctx: RunContext):
        return {"success": True}

    register_hook("pre", pre_hook)
    clear_hooks("pre")
    result = await _run_local("test_flow")
    assert result["success"] is True
    assert hook_called == []  # Hook should not be called


@pytest.mark.asyncio
async def test_clear_all_hooks():
    """Test clear_hooks() without args clears all hooks."""
    hook_called = []

    async def pre_hook(ctx: RunContext, flow_name: str, params: dict) -> None:
        hook_called.append("pre")

    async def post_hook(ctx: RunContext, result: dict) -> None:
        hook_called.append("post")

    @decorators.flow("test_flow")
    async def f(ctx: RunContext):
        return {"success": True}

    register_hook("pre", pre_hook)
    register_hook("post", post_hook)
    clear_hooks()
    result = await _run_local("test_flow")
    assert result["success"] is True
    assert hook_called == []  # No hooks should be called


@pytest.mark.asyncio
async def test_register_hook_invalid_type():
    """Test register_hook raises ValueError for invalid hook_type."""

    async def hook(ctx: RunContext, flow_name: str, params: dict) -> None:
        pass

    with pytest.raises(ValueError, match="hook_type must be 'pre' or 'post'"):
        register_hook("invalid", hook)


@pytest.mark.asyncio
async def test_clear_hooks_invalid_type():
    """Test clear_hooks raises ValueError for invalid hook_type."""
    with pytest.raises(ValueError, match="hook_type must be None, 'pre', or 'post'"):
        clear_hooks("invalid")


@pytest.mark.asyncio
async def test_post_hook_error_path_in_run_local():
    """Test post-hook error handling in _run_local error path."""
    hook_called = []

    async def failing_post_hook(ctx: RunContext, result: dict) -> None:
        hook_called.append("called")
        raise RuntimeError("Post-hook error")

    @decorators.flow("test_flow")
    async def f(ctx: RunContext):
        raise RuntimeError("Flow failed")

    register_hook("post", failing_post_hook)
    result = await _run_local("test_flow")
    # Execution should fail, but post-hook error should be ignored
    assert result["success"] is False
    assert hook_called == ["called"]  # Post-hook should be called
