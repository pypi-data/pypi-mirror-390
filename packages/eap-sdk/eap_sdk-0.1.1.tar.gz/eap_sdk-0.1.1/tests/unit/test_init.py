import os


def test_init_exports_and_version():
    # Test that __all__ and __version__ are defined by reading the file
    init_file = os.path.join(os.path.dirname(__file__), "../../src/eap_sdk/__init__.py")

    with open(init_file, encoding="utf-8") as f:
        content = f.read()

    # Verify __all__ is defined with expected exports (including task)
    assert "task" in content
    assert "__all__" in content
    # Verify __version__ is defined
    assert "__version__" in content
    assert '__version__ = "0.1.0"' in content
