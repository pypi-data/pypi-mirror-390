from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any


def _default_cleanup_fns() -> list[Callable[[], Awaitable[None]]]:
    """Default factory for cleanup functions list."""
    return []


@dataclass
class RunContext:
    run_id: str
    tenant: str | None = None
    labels: dict[str, str] = field(default_factory=dict)  # type: ignore[assignment]
    services: dict[str, Any] = field(default_factory=dict)  # type: ignore[assignment]
    _cleanup_fns: list[Callable[[], Awaitable[None]]] = field(
        default_factory=_default_cleanup_fns, init=False, repr=False
    )

    def get(self, key: str) -> Any:
        return self.services[key]

    def set(self, key: str, value: Any) -> None:
        self.services[key] = value

    def register_cleanup(self, cleanup_fn: Callable[[], Awaitable[None]]) -> None:
        """
        Register a cleanup function to be called after execution.

        Cleanup functions are called in reverse order of registration (LIFO).
        This allows proper cleanup of resources that depend on each other.

        Args:
            cleanup_fn: Async function that performs cleanup (no arguments)

        Example:
            async def pre_hook(ctx: RunContext, flow_name: str, params: dict) -> None:
                api = A2000Api(settings)
                await api.__aenter__()
                ctx.set("api", api)
                ctx.register_cleanup(lambda: api.__aexit__(None, None, None))
        """
        self._cleanup_fns.append(cleanup_fn)

    async def _run_cleanup(self) -> None:
        """Execute all registered cleanup functions in reverse order."""
        for cleanup_fn in reversed(self._cleanup_fns):
            try:
                await cleanup_fn()
            except Exception:
                # Log but don't fail - cleanup errors shouldn't break execution
                import logging

                logging.warning(f"Cleanup function failed: {cleanup_fn}", exc_info=True)
