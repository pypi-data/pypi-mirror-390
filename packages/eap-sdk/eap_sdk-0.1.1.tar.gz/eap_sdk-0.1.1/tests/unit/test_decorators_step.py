import asyncio
import time

import pytest

from eap_sdk import decorators


@pytest.mark.asyncio
async def test_step_async_success_and_metrics(monkeypatch):
    called = {"dur": [], "retries": 0}

    monkeypatch.setattr(
        decorators, "record_step_duration", lambda name, sec: called["dur"].append((name, sec))
    )
    monkeypatch.setattr(
        decorators,
        "inc_step_retries",
        lambda name: called.__setitem__("retries", called["retries"] + 1),
    )

    @decorators.step()
    async def work(x):
        await asyncio.sleep(0)
        return x * 2

    res = await work(3)
    assert res == 6
    assert called["dur"][0][0] == "work"


@pytest.mark.asyncio
async def test_step_sync_success_and_timeout(monkeypatch):
    # make the sync function run through asyncio.to_thread path
    @decorators.step(timeout_s=0.2)
    def slow():
        time.sleep(0.05)
        return 1

    assert await slow() == 1


@pytest.mark.asyncio
async def test_step_retries_with_backoff(monkeypatch):
    sleeps = []

    async def mock_sleep(delay):
        sleeps.append(delay)

    monkeypatch.setattr("asyncio.sleep", mock_sleep)
    monkeypatch.setattr(decorators.random, "uniform", lambda a, b: 0.0)
    attempts = {"n": 0}

    @decorators.step(retries=2, base_delay=0.1, backoff=2.0, jitter=0.0)
    async def flaky():
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise RuntimeError("fail")
        return "ok"

    res = await flaky()
    assert res == "ok"
    # two sleeps for two retries
    assert len(sleeps) == 2
    assert pytest.approx(sleeps[0], rel=1e-3) == 0.1
    assert pytest.approx(sleeps[1], rel=1e-3) == 0.2


@pytest.mark.asyncio
async def test_step_async_with_timeout(monkeypatch):
    @decorators.step(timeout_s=0.2)
    async def fast():
        await asyncio.sleep(0.01)
        return "done"

    result = await fast()
    assert result == "done"


@pytest.mark.asyncio
async def test_step_sync_without_timeout(monkeypatch):
    @decorators.step()
    def sync_func():
        return 42

    result = await sync_func()
    assert result == 42


@pytest.mark.asyncio
async def test_step_exhausts_retries(monkeypatch):
    sleeps = []

    async def mock_sleep(delay):
        sleeps.append(delay)

    monkeypatch.setattr("asyncio.sleep", mock_sleep)
    monkeypatch.setattr(decorators.random, "uniform", lambda a, b: 0.0)

    @decorators.step(retries=2, base_delay=0.01)
    async def always_fails():
        raise RuntimeError("always fails")

    with pytest.raises(RuntimeError, match="always fails"):
        await always_fails()

    # Should have slept for retries attempts
    assert len(sleeps) == 2
