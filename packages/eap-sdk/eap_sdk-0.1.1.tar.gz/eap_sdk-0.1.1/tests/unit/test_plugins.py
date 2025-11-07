import types

from eap_sdk import plugins


def test_register_and_build_services():
    # isolate registry
    plugins._SERVICE_FACTORIES.clear()

    created = {}

    def factory(ctx):
        created["called_with"] = ctx
        return {"ok": True}

    plugins.register_service("svc", factory)
    services = plugins.build_services(context={"ctx": 1})
    assert "svc" in services and services["svc"] == {"ok": True}
    assert created["called_with"] == {"ctx": 1}


def test_import_plugins_from_env_success_and_skip(monkeypatch):
    # set up a fake module that registers a service when imported
    mod_name = "fake_plugin_mod"
    mod = types.ModuleType(mod_name)

    def _reg_on_import():
        plugins.register_service("p_svc", lambda ctx: "plugged")

    mod.__dict__["__loader__"] = True
    mod.__dict__["__file__"] = __file__
    mod.__dict__["_init"] = _reg_on_import

    # Inject behavior on import by executing the register
    def import_hook(name):
        if name == mod_name:
            _reg_on_import()
            return mod
        raise ImportError

    # Clear registry and prepare env
    plugins._SERVICE_FACTORIES.clear()
    monkeypatch.setenv("EAP_PLUGINS", f"{mod_name},nonexistent.module")
    monkeypatch.setattr(plugins, "import_module", lambda name: import_hook(name))

    plugins.import_plugins_from_env()
    services = plugins.build_services(context=None)
    assert "p_svc" in services and services["p_svc"] == "plugged"
