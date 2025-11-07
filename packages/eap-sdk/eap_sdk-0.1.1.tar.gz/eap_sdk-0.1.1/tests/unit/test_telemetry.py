import importlib
import sys
import types


def test_telemetry_with_stubs(monkeypatch):
    # Provide stub prometheus_client before import
    class StubCounter:
        def __init__(self, *a, **k):
            self.labels_calls = []

        def labels(self, *values):
            self.labels_calls.append(values)
            return self

        def inc(self):
            self.inc_called = True

    class StubHistogram(StubCounter):
        def observe(self, v):
            self.observed = v

    stub = types.SimpleNamespace(Counter=StubCounter, Histogram=StubHistogram)
    monkeypatch.setitem(sys.modules, "prometheus_client", stub)

    import eap_sdk.telemetry as tel

    importlib.reload(tel)

    tel.record_job("f", "local", ok=False, err="E")
    tel.record_step_duration("s", 0.1)
    tel.inc_step_retries("s")

    # We can't access stubs directly from tel, but ensure no exceptions and functions exist
    assert (
        callable(tel.record_job)
        and callable(tel.record_step_duration)
        and callable(tel.inc_step_retries)
    )


def test_telemetry_without_prometheus(monkeypatch):
    # Simulate missing client
    import sys

    monkeypatch.setitem(sys.modules, "prometheus_client", None)
    import importlib as _il

    import eap_sdk.telemetry as tel

    _il.reload(tel)

    # Calls should be no-ops (no exceptions)
    tel.record_job("f", "local", ok=True)
    tel.record_step_duration("s", 0.2)
    tel.inc_step_retries("s")
