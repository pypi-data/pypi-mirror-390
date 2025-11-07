from __future__ import annotations

# Optional Prometheus client. If missing, fall back to no-ops.
try:
    from prometheus_client import Counter, Histogram  # type: ignore[import-untyped]
except Exception:  # pragma: no cover
    Counter = None
    Histogram = None

_jobs = Counter("eap_jobs_total", "Total jobs", ["flow", "runner"]) if Counter else None  # type: ignore[assignment]
_jobs_failed = (  # type: ignore[assignment]
    Counter("eap_jobs_failed_total", "Failed jobs", ["flow", "runner", "error"])
    if Counter
    else None
)
_step_hist = (  # type: ignore[assignment]
    Histogram("eap_step_duration_seconds", "Step duration", ["step"]) if Histogram else None
)
_step_retries = Counter("eap_step_retries_total", "Step retries", ["step"]) if Counter else None  # type: ignore[assignment]


def record_job(flow: str, runner: str, ok: bool, err: str | None = None) -> None:
    if _jobs:
        _jobs.labels(flow, runner).inc()  # type: ignore[union-attr]
    if not ok and _jobs_failed:
        _jobs_failed.labels(flow, runner, err or "Error").inc()  # type: ignore[union-attr]


def record_step_duration(step: str, sec: float) -> None:
    if _step_hist:
        _step_hist.labels(step).observe(sec)  # type: ignore[union-attr]


def inc_step_retries(step: str) -> None:
    if _step_retries:
        _step_retries.labels(step).inc()  # type: ignore[union-attr]
