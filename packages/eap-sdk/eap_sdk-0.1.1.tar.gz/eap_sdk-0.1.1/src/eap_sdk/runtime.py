from __future__ import annotations

import asyncio
import logging
import os
import uuid
from collections.abc import Awaitable, Callable
from typing import Any, Protocol

import httpx

from .context import RunContext
from .contracts import RunRequest, RunResponse
from .decorators import get_flow
from .plugins import build_services, import_plugins_from_env
from .telemetry import record_job

# Hook registry: maps hook type ("pre" or "post") to list of hook functions
_HOOKS: dict[str, list[Callable[..., Awaitable[None]]]] = {"pre": [], "post": []}


def build_flow_spec(flow_fn: Any, flow_name: str) -> dict[str, Any]:
    """
    Build flow specification dictionary for remote execution.
    For now, creates a minimal spec with a single task representing the flow.
    """
    from .decorators import _infer_entrypoint  # type: ignore[import-private] # noqa: PLC0415

    entrypoint = getattr(flow_fn, "_eap_flow_entry", None)
    if entrypoint is None:
        entrypoint = _infer_entrypoint(flow_fn)

    return {
        "flow_id": f"py.{flow_name}",
        "version": 1,
        "tasks": [
            {
                "id": "task-1",
                "name": flow_name,
                "entrypoint": entrypoint,
            }
        ],
    }


# Transport SPI
class Transport(Protocol):
    async def run(self, flow: str, params: dict[str, Any]) -> dict[str, Any]: ...


class LocalTransport:
    async def run(self, flow: str, params: dict[str, Any]) -> dict[str, Any]:
        return await _run_local(flow, **params)


class HTTPTransport:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def run(self, flow: str, params: dict[str, Any]) -> dict[str, Any]:
        ctx = RunContext(run_id=str(uuid.uuid4()), tenant=os.getenv("EAP_TENANT"))

        # Pre-execution hooks
        for hook in _HOOKS["pre"]:
            try:
                await hook(ctx, flow, params)  # type: ignore[call-arg]
            except Exception as e:
                return RunResponse(
                    success=False,
                    message=f"Pre-execution hook failed: {e}",
                    error=str(e),
                ).model_dump()

        try:
            async with httpx.AsyncClient(
                timeout=float(os.getenv("EAP_HTTP_TIMEOUT", "60"))
            ) as client:
                try:
                    body = RunRequest(flow=flow, params=params).model_dump()
                    r = await client.post(f"{self.base_url}/run", json=body)
                    r.raise_for_status()
                    result = r.json()
                except httpx.HTTPError as e:
                    result = RunResponse(
                        success=False, message="HTTP error", error=str(e)
                    ).model_dump()

            # Post-execution hooks (called on both success and error)
            for hook in _HOOKS["post"]:
                try:
                    await hook(ctx, result)  # type: ignore[call-arg]
                except Exception as hook_error:
                    # Log but don't fail the flow execution
                    logging.warning(f"Post-execution hook failed: {hook_error}", exc_info=True)

            # Run cleanup functions
            await ctx._run_cleanup()  # type: ignore[reportPrivateUsage]

            return result
        except Exception as e:
            # If something fails outside HTTP call, still run cleanup
            error_result = RunResponse(
                success=False, message="Transport error", error=str(e)
            ).model_dump()

            # Post-execution hooks
            for hook in _HOOKS["post"]:
                try:
                    await hook(ctx, error_result)  # type: ignore[call-arg]
                except Exception:
                    pass

            # Run cleanup functions even on error
            await ctx._run_cleanup()  # type: ignore[reportPrivateUsage]

            return error_result


def submit_remote_http(
    base: str,
    flow_spec: dict[str, Any],
    deployment: dict[str, Any],
    params: dict[str, Any],
) -> str:
    """
    Submit flow execution request to remote Maestro HTTP endpoint.
    Uses new flow spec format with spec/deployment/params.
    Returns run_id string.
    """
    url = f"{base.rstrip('/')}/run"
    payload = {
        "spec": flow_spec,
        "deployment": deployment,
        "params": params,
    }

    response = httpx.post(url, json=payload, timeout=10.0)
    response.raise_for_status()
    data = response.json()

    if not data.get("success"):
        raise RuntimeError(f"Remote run failed: {data}")

    run_id = data.get("run_id")
    if not run_id:
        raise RuntimeError(f"Response missing run_id: {data}")

    return str(run_id)


# Hook API
def register_hook(
    hook_type: str,
    hook_fn: Callable[[RunContext, str, dict[str, Any]], Awaitable[None]]
    | Callable[[RunContext, dict[str, Any]], Awaitable[None]],
) -> None:
    """
    Register a lifecycle hook.

    Args:
        hook_type: Either 'pre' or 'post'
        hook_fn: Async function to call

    Pre-execution hooks:
        async def pre_hook(ctx: RunContext, flow_name: str, params: dict[str, Any]) -> None:
            # Setup before flow execution
            pass

    Post-execution hooks:
        async def post_hook(ctx: RunContext, result: dict[str, Any]) -> None:
            # Cleanup after flow execution
            pass
    """
    if hook_type not in ("pre", "post"):
        raise ValueError(f"hook_type must be 'pre' or 'post', got {hook_type}")
    _HOOKS[hook_type].append(hook_fn)  # type: ignore[arg-type]


def clear_hooks(hook_type: str | None = None) -> None:
    """
    Clear registered hooks.

    Args:
        hook_type: If None, clears all hooks. If 'pre' or 'post', clears only that type.
    """
    if hook_type is None:
        _HOOKS["pre"].clear()
        _HOOKS["post"].clear()
    elif hook_type in _HOOKS:
        _HOOKS[hook_type].clear()
    else:
        raise ValueError(f"hook_type must be None, 'pre', or 'post', got {hook_type}")


# Public API
def serve(*_args: Any, **_kwargs: Any) -> None:
    """
    Placeholder for future registration with Maestro. No-op in B1/B2.
    Kept to maintain API continuity.
    """
    return None


def run(flow: str, runner: str = "local", **params: Any) -> dict[str, Any]:
    """
    Synchronous helper for scripts/CLI.
    """
    return asyncio.run(arun(flow, runner=runner, **params))


async def arun(flow: str, runner: str = "local", **params: Any) -> dict[str, Any]:
    """
    Async variant. Selects transport by 'runner' or environment.
    """
    import_plugins_from_env()  # EAP_PLUGINS="pkg.module,another.module"

    if runner == "remote" or os.getenv("MAESTRO_ADDR") or os.getenv("ROBOT_ADDR"):
        base = os.getenv("MAESTRO_ADDR") or os.getenv("ROBOT_ADDR")
        if not base:
            return RunResponse(
                success=False,
                message="Remote runner requires MAESTRO_ADDR or ROBOT_ADDR",
                error="ConfigError",
            ).model_dump()
        transport: Transport = HTTPTransport(base)
        resp = await transport.run(flow, params)
        ok = bool(resp.get("success"))
        record_job(flow, "remote", ok, resp.get("error"))
        return resp

    # default local
    resp = await _run_local(flow, **params)
    ok = bool(resp.get("success"))
    record_job(flow, "local", ok, resp.get("error"))
    return resp


# Internal local execution
async def _run_local(flow_name: str, **params: Any) -> dict[str, Any]:
    try:
        fn = get_flow(flow_name)
    except KeyError as e:
        return RunResponse(success=False, message=str(e), error="UnknownFlow").model_dump()

    ctx = RunContext(run_id=str(uuid.uuid4()), tenant=os.getenv("EAP_TENANT"))

    # Pre-execution hooks
    for hook in _HOOKS["pre"]:
        try:
            await hook(ctx, flow_name, params)  # type: ignore[call-arg]
        except Exception as e:
            return RunResponse(
                success=False,
                message=f"Pre-execution hook failed: {e}",
                error=str(e),
            ).model_dump()

    ctx.services.update(build_services(ctx))

    try:
        data = await fn(ctx, **params)
        if not isinstance(data, dict):  # type: ignore[redundant-expr]
            # normalize
            data = {"result": data}
        result = RunResponse(success=True, message="OK", data=data).model_dump()

        # Post-execution hooks (called on success)
        for hook in _HOOKS["post"]:
            try:
                await hook(ctx, result)  # type: ignore[call-arg]
            except Exception as hook_error:
                # Log but don't fail the flow execution
                logging.warning(f"Post-execution hook failed: {hook_error}", exc_info=True)

        # Run cleanup functions
        await ctx._run_cleanup()  # type: ignore[reportPrivateUsage]

        return result
    except Exception as e:
        # Include traceback if EAP_DEBUG=1
        import traceback

        if os.getenv("EAP_DEBUG") == "1":
            tb = traceback.format_exc()
            error_result = RunResponse(success=False, message="Flow failed", error=tb).model_dump()
        else:
            error_result = RunResponse(
                success=False, message="Flow failed", error=str(e)
            ).model_dump()

        # Post-execution hooks (called on error too)
        for hook in _HOOKS["post"]:
            try:
                await hook(ctx, error_result)  # type: ignore[call-arg]
            except Exception:
                # Ignore cleanup errors
                pass

        # Run cleanup functions even on error
        await ctx._run_cleanup()  # type: ignore[reportPrivateUsage]

        return error_result


def run_entrypoint(entry: str, kwargs: dict[str, Any]) -> Any:
    """
    Execute a flow entrypoint string in 'module:func' format.
    Used by robots for remote execution.
    """
    import importlib

    module_name, func_name = entry.split(":", 1)
    mod = importlib.import_module(module_name)
    func_obj = getattr(mod, func_name)
    return func_obj(**kwargs)
