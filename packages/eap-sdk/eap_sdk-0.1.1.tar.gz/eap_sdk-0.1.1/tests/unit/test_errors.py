import pytest

from eap_sdk.errors import ConfigError, SDKError, TransportError, UnknownFlow


def test_sdk_error_hierarchy():
    assert issubclass(UnknownFlow, SDKError)
    assert issubclass(TransportError, SDKError)
    assert issubclass(ConfigError, SDKError)
    assert issubclass(SDKError, RuntimeError)


def test_sdk_errors_can_be_raised():
    with pytest.raises(UnknownFlow):
        raise UnknownFlow("test")

    with pytest.raises(TransportError):
        raise TransportError("test")

    with pytest.raises(ConfigError):
        raise ConfigError("test")

    with pytest.raises(SDKError):
        raise SDKError("test")
