"""Tests for @task decorator alias."""

import asyncio

import pytest

from eap_sdk import decorators, task


@pytest.mark.asyncio
async def test_task_is_step_alias():
    """Test that @task is an alias for @step."""

    @task(retries=2)
    async def task_func(x):
        return x * 2

    @decorators.step(retries=2)
    async def step_func(x):
        return x * 2

    assert await task_func(5) == 10
    assert await step_func(5) == 10


@pytest.mark.asyncio
async def test_task_retries():
    """Test that @task has the same retry behavior as @step."""
    attempts = {"count": 0}

    @task(retries=2, base_delay=0.01)
    async def flaky_task():
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise RuntimeError("fail")
        return "success"

    result = await flaky_task()
    assert result == "success"
    assert attempts["count"] == 3


@pytest.mark.asyncio
async def test_task_timeout():
    """Test that @task supports timeout like @step."""

    @task(timeout_s=0.1)
    async def quick_task():
        await asyncio.sleep(0.01)
        return "done"

    result = await quick_task()
    assert result == "done"


def test_task_importable():
    """Test that task is importable from main package."""
    from eap_sdk import task as imported_task

    assert imported_task is task
    assert callable(imported_task)
