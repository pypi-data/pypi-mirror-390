"""Tests for run_entrypoint helper function."""

import pytest

from eap_sdk import runtime


def test_run_entrypoint_executes_function():
    """Test that run_entrypoint can execute a function by entrypoint."""

    def test_func(x: int, y: str) -> dict:
        return {"result": x, "text": y}

    # Create a test module in memory
    import sys
    import types

    test_module = types.ModuleType("test_module")
    test_module.test_func = test_func
    sys.modules["test_module"] = test_module

    try:
        result = runtime.run_entrypoint("test_module:test_func", {"x": 42, "y": "hello"})
        assert result == {"result": 42, "text": "hello"}
    finally:
        # Clean up
        if "test_module" in sys.modules:
            del sys.modules["test_module"]


def test_run_entrypoint_raises_on_invalid_format():
    """Test that run_entrypoint raises error on invalid entrypoint format."""
    with pytest.raises(ValueError):
        runtime.run_entrypoint("invalid_format", {})


def test_run_entrypoint_raises_on_missing_module():
    """Test that run_entrypoint raises error on missing module."""
    with pytest.raises(ImportError):
        runtime.run_entrypoint("nonexistent_module:func", {})


def test_run_entrypoint_raises_on_missing_function():
    """Test that run_entrypoint raises error on missing function."""
    import sys
    import types

    test_module = types.ModuleType("test_module2")
    sys.modules["test_module2"] = test_module

    try:
        with pytest.raises(AttributeError):
            runtime.run_entrypoint("test_module2:nonexistent_func", {})
    finally:
        if "test_module2" in sys.modules:
            del sys.modules["test_module2"]
