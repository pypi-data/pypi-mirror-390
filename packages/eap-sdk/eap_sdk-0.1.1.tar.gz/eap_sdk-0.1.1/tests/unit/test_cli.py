import argparse
import json

from eap_sdk.cli import coerce_value, main, parse_params


def test_cli_run_success_and_param_coercion(monkeypatch, capsys):
    def fake_run(flow, runner="local", **params):
        return {"success": True, "message": "OK", "data": params}

    import eap_sdk.cli as cli

    monkeypatch.setattr(cli, "run_sync", fake_run)

    code = main(
        [
            "run",
            "flow",
            "--runner",
            "local",
            "--param",
            "a=1",
            "--param",
            "b=true",
            "--param-json",
            '{"c":2}',
        ]
    )
    assert code == 0
    out = capsys.readouterr().out
    doc = json.loads(out)
    assert doc["success"] is True
    assert doc["data"] == {"a": 1, "b": True, "c": 2}


def test_cli_run_failure_exit_code(monkeypatch, capsys):
    def fake_run(flow, runner="local", **params):
        return {"success": False, "message": "bad"}

    import eap_sdk.cli as cli

    monkeypatch.setattr(cli, "run_sync", fake_run)
    code = main(["run", "x"])  # minimal
    assert code == 1


def test_cli_param_json_non_dict(monkeypatch, capsys):
    def fake_run(flow, runner="local", **params):
        return {"success": True, "data": params}

    import eap_sdk.cli as cli

    monkeypatch.setattr(cli, "run_sync", fake_run)

    code = main(["run", "flow", "--param-json", "[1,2,3]"])
    assert code == 0
    out = capsys.readouterr().out
    doc = json.loads(out)
    assert doc["data"] == {}


def test_cli_param_json_malformed(monkeypatch, capsys):
    def fake_run(flow, runner="local", **params):
        return {"success": True, "data": params}

    import eap_sdk.cli as cli

    monkeypatch.setattr(cli, "run_sync", fake_run)

    code = main(["run", "flow", "--param-json", "{invalid json"])
    assert code == 0
    out = capsys.readouterr().out
    doc = json.loads(out)
    assert doc["data"] == {}


def test_cli_param_without_equals(monkeypatch, capsys):
    def fake_run(flow, runner="local", **params):
        return {"success": True, "data": params}

    import eap_sdk.cli as cli

    monkeypatch.setattr(cli, "run_sync", fake_run)

    code = main(["run", "flow", "--param", "noequals"])
    assert code == 0
    out = capsys.readouterr().out
    doc = json.loads(out)
    assert doc["data"] == {}


def test_cli_param_coercion_numeric(monkeypatch, capsys):
    def fake_run(flow, runner="local", **params):
        return {"success": True, "data": params}

    import eap_sdk.cli as cli

    monkeypatch.setattr(cli, "run_sync", fake_run)

    code = main(["run", "flow", "--param", "x=42", "--param", "y=3.14"])
    assert code == 0
    out = capsys.readouterr().out
    doc = json.loads(out)
    assert doc["data"] == {"x": 42, "y": 3.14}


def test_cli_param_coercion_string_fallback(monkeypatch, capsys):
    def fake_run(flow, runner="local", **params):
        return {"success": True, "data": params}

    import eap_sdk.cli as cli

    monkeypatch.setattr(cli, "run_sync", fake_run)

    # Test string that can't be parsed as JSON or number
    code = main(["run", "flow", "--param", "x=hello"])
    assert code == 0
    out = capsys.readouterr().out
    doc = json.loads(out)
    assert doc["data"] == {"x": "hello"}


# Tests for extracted coerce_value() function
def test_coerce_value_json_bool():
    assert coerce_value("true") is True
    assert coerce_value("false") is False


def test_coerce_value_json_null():
    assert coerce_value("null") is None


def test_coerce_value_json_number():
    assert coerce_value("42") == 42
    assert coerce_value("3.14") == 3.14
    assert coerce_value("-10") == -10


def test_coerce_value_json_array():
    assert coerce_value("[1,2,3]") == [1, 2, 3]
    assert coerce_value('["a","b"]') == ["a", "b"]


def test_coerce_value_json_object():
    assert coerce_value('{"a":1}') == {"a": 1}
    assert coerce_value('{"x":true,"y":false}') == {"x": True, "y": False}


def test_coerce_value_numeric_fallback():
    assert coerce_value("42") == 42
    assert coerce_value("3.14") == 3.14


def test_coerce_value_string_fallback():
    assert coerce_value("hello") == "hello"
    assert coerce_value("test-value") == "test-value"


def test_coerce_value_malformed_json():
    # Malformed JSON should fall back to string
    assert coerce_value("{invalid") == "{invalid"
    assert coerce_value("[unclosed") == "[unclosed"


# Tests for extracted parse_params() function
def test_parse_params_from_param_args():
    args = argparse.Namespace(param=["a=1", "b=true", "c=hello"], param_json=None)
    result = parse_params(args)
    assert result == {"a": 1, "b": True, "c": "hello"}


def test_parse_params_from_param_json():
    args = argparse.Namespace(param=[], param_json='{"x": 42, "y": "test"}')
    result = parse_params(args)
    assert result == {"x": 42, "y": "test"}


def test_parse_params_combined():
    args = argparse.Namespace(param=["a=1", "b=true"], param_json='{"c": 2, "d": "json"}')
    result = parse_params(args)
    assert result == {"a": 1, "b": True, "c": 2, "d": "json"}


def test_parse_params_param_overrides_json():
    # --param should override --param-json if same key
    args = argparse.Namespace(param=["a=overridden"], param_json='{"a": "original", "b": 2}')
    result = parse_params(args)
    assert result == {"a": "overridden", "b": 2}


def test_parse_params_missing_equals():
    args = argparse.Namespace(param=["noequals", "valid=value"], param_json=None)
    result = parse_params(args)
    assert result == {"valid": "value"}


def test_parse_params_malformed_json():
    args = argparse.Namespace(param=[], param_json="{invalid json")
    result = parse_params(args)
    assert result == {}


def test_parse_params_json_non_dict():
    # Non-dict JSON should be ignored
    args = argparse.Namespace(param=[], param_json="[1,2,3]")
    result = parse_params(args)
    assert result == {}


def test_parse_params_empty():
    args = argparse.Namespace(param=[], param_json=None)
    result = parse_params(args)
    assert result == {}
