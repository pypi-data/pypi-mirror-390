from __future__ import annotations

import os
from collections.abc import Callable
from importlib import import_module
from typing import Any

# name -> factory(ctx) -> instance
_SERVICE_FACTORIES: dict[str, Callable[[Any], Any]] = {}


def register_service(name: str, factory: Callable[[Any], Any]) -> None:
    """
    Apps/plugins call this at import-time to bind a service by name.
    """
    _SERVICE_FACTORIES[name] = factory


def build_services(context: Any) -> dict[str, Any]:
    return {n: f(context) for n, f in _SERVICE_FACTORIES.items()}


def import_plugins_from_env(env_key: str = "EAP_PLUGINS") -> None:
    """
    Load comma-separated module list from env (e.g., 'my_org.a2000_adapter,my_org.ps_adapter').
    Each module, when imported, should call register_service(...).
    """
    mods = os.getenv(env_key, "").strip()
    if not mods:
        return
    for mod in [m.strip() for m in mods.split(",") if m.strip()]:
        try:
            import_module(mod)
        except Exception:  # nosec B112 - Skip faulty plugin modules; do not block others
            # Skip faulty plugin modules; do not block others
            continue
