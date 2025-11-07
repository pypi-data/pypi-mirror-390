import pytest

from eap_sdk.blocks import HttpAuthBlock


def test_http_auth_block_from_env_defaults(monkeypatch):
    prefix = "TESTSDK"
    monkeypatch.delenv(f"{prefix}_BASE_URL", raising=False)
    monkeypatch.delenv(f"{prefix}_USER", raising=False)
    monkeypatch.delenv(f"{prefix}_PASS", raising=False)
    monkeypatch.delenv(f"{prefix}_VERIFY_TLS", raising=False)
    monkeypatch.delenv(f"{prefix}_TIMEOUT_S", raising=False)

    block = HttpAuthBlock.from_env(prefix)
    assert block.base_url == ""
    assert block.username is None
    assert block.password is None
    assert block.verify_tls is True
    assert block.timeout_s == 30.0


@pytest.mark.parametrize(
    "verify,timeout,expect_verify,expect_timeout",
    [
        ("true", "15", True, 15.0),
        ("false", "5.5", False, 5.5),
        ("TRUE", "60", True, 60.0),
    ],
)
def test_http_auth_block_from_env_coercions(
    monkeypatch, verify, timeout, expect_verify, expect_timeout
):
    prefix = "TESTSDK"
    monkeypatch.setenv(f"{prefix}_BASE_URL", "https://example.local/")
    monkeypatch.setenv(f"{prefix}_USER", "u")
    monkeypatch.setenv(f"{prefix}_PASS", "p")
    monkeypatch.setenv(f"{prefix}_VERIFY_TLS", verify)
    monkeypatch.setenv(f"{prefix}_TIMEOUT_S", timeout)

    block = HttpAuthBlock.from_env(prefix)
    assert block.base_url == "https://example.local/"
    assert block.username == "u"
    assert block.password == "p"
    assert block.verify_tls is expect_verify
    assert block.timeout_s == pytest.approx(expect_timeout)
