from eap_sdk.contracts import RunRequest, RunResponse


def test_run_request_and_response_models():
    rr = RunRequest(flow="demo", params={"a": 1})
    dumped = rr.model_dump()
    assert dumped["flow"] == "demo"
    assert dumped["params"] == {"a": 1}

    resp = RunResponse(success=True, message="OK", data={"x": 2}, error=None)
    d2 = resp.model_dump()
    assert d2["success"] is True
    assert d2["message"] == "OK"
    assert d2["data"] == {"x": 2}
    assert d2["error"] is None
