from __future__ import annotations

import asyncio
import functools
import inspect
import os
import random
import time
from collections.abc import Awaitable, Callable
from typing import Any

from .telemetry import inc_step_retries, record_step_duration

# Flow registry
_FLOWS: dict[str, Callable[..., Awaitable[dict[str, Any]]]] = {}


def _infer_entrypoint(fn: Callable[..., Any]) -> str:
    """Infer entrypoint string in 'module:func' format."""
    module = inspect.getmodule(fn)
    if module is None:
        # Fallback if module cannot be determined
        return f"__main__:{fn.__name__}"
    module_name = module.__name__
    return f"{module_name}:{fn.__name__}"


def flow(name: str | None = None):
    """
    Decorate an async function(ctx: RunContext, **params) -> dict
    Registers it under the provided name or the function's __name__.
    Stores entrypoint in 'module:func' format for remote execution.
    Attaches .serve() method for remote execution.
    """

    def deco(fn: Callable[..., Awaitable[dict[str, Any]]]):
        if not inspect.iscoroutinefunction(fn):
            raise TypeError("@flow requires an async function")

        reg_name = name or fn.__name__
        if reg_name in _FLOWS:
            raise ValueError(f"Flow '{reg_name}' already registered")

        # Infer and store entrypoint
        entrypoint = _infer_entrypoint(fn)
        fn._eap_flow_entry = entrypoint  # type: ignore[assignment]

        # Register by name
        _FLOWS[reg_name] = fn
        # Also register by entrypoint for lookup
        _FLOWS[entrypoint] = fn

        # Attach serve() method for remote execution
        def serve(
            pool: str,
            schedule: str | None = None,
            params: dict[str, Any] | None = None,
        ) -> str:
            """
            Submit flow for remote execution via Maestro HTTP endpoint.
            Returns run_id string.
            """
            # Import here to avoid circular dependency
            from .runtime import build_flow_spec, submit_remote_http

            http = os.getenv("MAESTRO_HTTP")
            if not http:
                raise RuntimeError("Set MAESTRO_HTTP=http://localhost:8080 to use remote submit")

            flow_spec = build_flow_spec(fn, reg_name)
            deployment = {
                "pool": pool,
                "schedule": schedule or "",
                "defaults": params or {},
            }
            run_id = submit_remote_http(http, flow_spec, deployment, params or {})
            return run_id

        fn.serve = serve  # type: ignore[attr-defined]

        return fn

    return deco


def get_flow(name: str) -> Callable[..., Awaitable[dict[str, Any]]]:
    """
    Get flow by name or entrypoint.
    Supports both name-based ('my_flow') and entrypoint-based ('module:func') lookup.
    """
    fn = _FLOWS.get(name)
    if not fn:
        raise KeyError(f"Unknown flow '{name}'")
    return fn


# Step decorator (retry/timeout)
def step(
    retries: int = 0,
    timeout_s: float | None = None,
    backoff: float = 1.5,
    base_delay: float = 0.5,
    jitter: float = 0.2,
):
    """
    Decorate a sync or async step function. First argument MAY be RunContext (recommended).
    The wrapper normalizes execution and applies retry/timeout with jitter.
    """

    def deco(fn: Callable[..., Any]):
        @functools.wraps(fn)
        async def wrapped(*args: Any, **kwargs: Any) -> Any:
            attempt = 0
            while True:
                attempt += 1
                t0 = time.perf_counter()
                try:
                    if inspect.iscoroutinefunction(fn):
                        coro = fn(*args, **kwargs)
                        if timeout_s:
                            result = await asyncio.wait_for(coro, timeout=timeout_s)
                        else:
                            result = await coro
                    else:
                        # Run sync function in a thread to avoid blocking the event loop
                        if timeout_s is not None:
                            result = await asyncio.wait_for(
                                asyncio.to_thread(fn, *args, **kwargs), timeout=timeout_s
                            )
                        else:
                            result = await asyncio.to_thread(fn, *args, **kwargs)
                    record_step_duration(fn.__name__, time.perf_counter() - t0)
                    return result
                except Exception:
                    if attempt > retries:
                        raise
                    inc_step_retries(fn.__name__)
                    # exponential backoff + jitter
                    delay = base_delay * (backoff ** (attempt - 1))
                    delay += delay * random.uniform(-jitter, jitter)  # nosec B311 - jitter for backoff, not crypto
                    await asyncio.sleep(max(0.0, delay))

        return wrapped

    return deco


# Task decorator (alias for step)
task = step
