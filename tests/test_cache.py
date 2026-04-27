import os
import time

import numpy as np

import ctl
from ctl import _ctl_native


def test_cache_speedup(identity_ctl):
    a = np.array([[0.5, 0.5, 0.5]], dtype=np.float32)
    _ctl_native.cache_clear()
    t0 = time.perf_counter()
    _ctl_native.apply(a, [str(identity_ctl)], {})
    cold = time.perf_counter() - t0
    t0 = time.perf_counter()
    _ctl_native.apply(a, [str(identity_ctl)], {})
    warm = time.perf_counter() - t0
    # Warm hit should be meaningfully faster. Identity is trivial so the
    # ratio is loose to avoid timer-resolution flakes on CI.
    assert warm < cold * 0.8, f"cold={cold*1000:.2f}ms warm={warm*1000:.2f}ms"


def test_cache_info_lists_loaded(identity_ctl):
    _ctl_native.cache_clear()
    a = np.array([[0.5, 0.5, 0.5]], dtype=np.float32)
    _ctl_native.apply(a, [str(identity_ctl)], {})
    entries = _ctl_native.cache_info()
    paths = [e["path"] for e in entries]
    assert any(str(identity_ctl) in p for p in paths)


def test_cache_clear_empties(identity_ctl):
    a = np.array([[0.5, 0.5, 0.5]], dtype=np.float32)
    _ctl_native.apply(a, [str(identity_ctl)], {})
    _ctl_native.cache_clear()
    assert _ctl_native.cache_info() == []


def test_cache_invalidates_on_mtime_change(tmp_path):
    src = tmp_path / "tmp.ctl"
    src.write_text(
        "void main(varying float rIn, varying float gIn, varying float bIn,\n"
        "  output varying float rOut, output varying float gOut, output varying float bOut)\n"
        "{ rOut = rIn; gOut = gIn; bOut = bIn; }\n"
    )
    a = np.array([[0.5, 0.5, 0.5]], dtype=np.float32)
    out1 = _ctl_native.apply(a, [str(src)], {})
    np.testing.assert_array_almost_equal(out1, a)

    time.sleep(0.05)
    src.write_text(
        "void main(varying float rIn, varying float gIn, varying float bIn,\n"
        "  output varying float rOut, output varying float gOut, output varying float bOut)\n"
        "{ rOut = rIn * 2.0; gOut = gIn * 2.0; bOut = bIn * 2.0; }\n"
    )
    new_t = os.path.getmtime(src) + 1
    os.utime(src, (new_t, new_t))

    out2 = _ctl_native.apply(a, [str(src)], {})
    np.testing.assert_array_almost_equal(out2, a * 2)


def test_python_cache_info_returns_dataclass(identity_ctl):
    a = np.array([[0.5, 0.5, 0.5]], dtype=np.float32)
    ctl.apply(a, identity_ctl)
    entries = ctl.cache_info()
    assert any(str(identity_ctl) in e.path for e in entries)
    assert all(isinstance(e.mtime_ns, int) for e in entries)


def test_python_cache_clear(identity_ctl):
    a = np.array([[0.5, 0.5, 0.5]], dtype=np.float32)
    ctl.apply(a, identity_ctl)
    ctl.cache_clear()
    assert ctl.cache_info() == []


def test_cache_invalidates_on_import_change(tmp_path):
    """Editing an imported helper .ctl must invalidate the main file's cache entry."""
    helper = tmp_path / "imports" / "Lib.helper.ctl"
    helper.parent.mkdir()
    helper.write_text("const float kScale = 2.0;\n")
    main_ctl = tmp_path / "uses.ctl"
    main_ctl.write_text(
        'import "Lib.helper";\n'
        "void main(varying float rIn, varying float gIn, varying float bIn,\n"
        "  output varying float rOut, output varying float gOut, output varying float bOut)\n"
        "{ rOut = rIn * kScale; gOut = gIn * kScale; bOut = bIn * kScale; }\n"
    )

    ctl.cache_clear()
    ctl.set_module_paths([str(helper.parent)])
    a = np.array([[0.1, 0.1, 0.1]], dtype=np.float32)

    out1 = ctl.apply(a, main_ctl)
    np.testing.assert_array_almost_equal(out1, a * 2)

    # Edit the import
    time.sleep(0.05)
    helper.write_text("const float kScale = 5.0;\n")
    new_t = os.path.getmtime(helper) + 1
    os.utime(helper, (new_t, new_t))

    out2 = ctl.apply(a, main_ctl)
    np.testing.assert_array_almost_equal(out2, a * 5)
