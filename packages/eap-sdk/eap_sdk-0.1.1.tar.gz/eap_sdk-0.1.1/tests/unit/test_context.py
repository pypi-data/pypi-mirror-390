from eap_sdk.context import RunContext


def test_run_context_defaults_and_get_set():
    ctx = RunContext(run_id="rid", tenant=None)
    assert ctx.labels == {}
    assert ctx.services == {}

    ctx.set("svc", 123)
    assert ctx.get("svc") == 123
