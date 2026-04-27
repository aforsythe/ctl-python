import pathlib

import numpy as np
import pytest

import ctl

FIXTURES = pathlib.Path(__file__).parent / "fixtures"


def test_module_path_via_setter():
    ctl.cache_clear()
    ctl.set_module_paths([str(FIXTURES / "imports")])
    a = np.array([[0.1, 0.1, 0.1]], dtype=np.float32)
    out = ctl.apply(a, FIXTURES / "uses_helper.ctl")
    np.testing.assert_array_almost_equal(out, a * 3)


def test_module_path_via_env(monkeypatch):
    monkeypatch.setenv("CTL_MODULE_PATH", str(FIXTURES / "imports"))
    ctl.cache_clear()
    ctl.set_module_paths([])  # clear user paths so env takes over
    a = np.array([[0.1, 0.1, 0.1]], dtype=np.float32)
    out = ctl.apply(a, FIXTURES / "uses_helper.ctl")
    np.testing.assert_array_almost_equal(out, a * 3)


def test_module_path_missing_raises(monkeypatch):
    monkeypatch.delenv("CTL_MODULE_PATH", raising=False)
    ctl.cache_clear()
    ctl.set_module_paths([])
    a = np.array([[0.1, 0.1, 0.1]], dtype=np.float32)
    with pytest.raises(ctl.CtlError):
        ctl.apply(a, FIXTURES / "uses_helper.ctl")
