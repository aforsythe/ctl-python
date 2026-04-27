def test_native_module_imports():
    from ctl import _ctl_native  # noqa: F401

def test_version_attribute():
    import ctl
    assert isinstance(ctl.__version__, str)
