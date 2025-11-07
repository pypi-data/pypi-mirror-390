from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .runtime import run as run_sync


def coerce_value(value: str) -> Any:
    """
    Coerce a string value to appropriate Python type.

    Tries JSON parsing first (handles bool, null, numbers, arrays, objects),
    then falls back to int, float, or returns string as-is.

    Args:
        value: String value to coerce

    Returns:
        Coerced value (bool, int, float, dict, list, None, or str)

    Examples:
        >>> coerce_value("true")
        True
        >>> coerce_value("42")
        42
        >>> coerce_value("3.14")
        3.14
        >>> coerce_value("hello")
        "hello"
    """
    # Try JSON first (handles bool, null, numbers, arrays)
    try:
        return json.loads(value)
    except Exception:  # nosec B110 - intentional fallback for non-JSON values
        pass
    # Fallback basic numeric coercion
    try:
        return int(value)
    except Exception:  # nosec B110 - intentional fallback for non-numeric values
        pass
    try:
        return float(value)
    except Exception:  # nosec B110 - intentional fallback for non-numeric values
        pass
    # Keep string as-is
    return value


def parse_params(args: argparse.Namespace) -> dict[str, Any]:
    """
    Parse parameters from argparse.Namespace.

    Extracts parameters from --param and --param-json arguments,
    merging them into a single dictionary.

    Args:
        args: Parsed argparse.Namespace with 'param' and 'param_json' attributes

    Returns:
        Dictionary of parsed and coerced parameters

    Examples:
        >>> args = argparse.Namespace(
        ...     param=["a=1", "b=true"],
        ...     param_json='{"c": 2}'
        ... )
        >>> parse_params(args)
        {"a": 1, "b": True, "c": 2}
    """
    params: dict[str, Any] = {}

    # Optional JSON blob
    if args.param_json:
        try:
            obj = json.loads(args.param_json)
            if isinstance(obj, dict):
                params.update(obj)  # type: ignore[arg-type]
        except Exception:  # nosec B110 - intentional fallback for malformed JSON
            pass

    # Parse --param k=v pairs
    for kv in args.param:
        if "=" not in kv:
            continue
        k, v = kv.split("=", 1)
        params[k] = coerce_value(v)

    return params


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser("eap-sdk", description="SDK runner")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="Run a registered flow")
    r.add_argument("flow", help="Flow name")
    r.add_argument("--runner", default="local", choices=["local", "remote"], help="Execution mode")
    r.add_argument("--param", action="append", default=[], help="k=v pairs (repeatable)")
    r.add_argument("--param-json", default=None, help="JSON object with parameters")
    args = p.parse_args(argv)

    if args.cmd == "run":
        params = parse_params(args)
        resp = run_sync(args.flow, runner=args.runner, **params)
        print(json.dumps(resp, indent=2, ensure_ascii=False))
        return 0 if resp.get("success") else 1

    return 2


if __name__ == "__main__":
    sys.exit(main())
