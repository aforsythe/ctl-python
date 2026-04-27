# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Alex Forsythe, Academy of Motion Picture Arts and Sciences
import numpy as np
import pytest

import ctl
from ctl import _ctl_native


def test_apply_identity_n3(identity_ctl):
    a = np.array([[0.0, 0.18, 0.5],
                  [1.0, 0.5,  0.25]], dtype=np.float32)
    out = _ctl_native.apply(a, [str(identity_ctl)], {})
    np.testing.assert_array_equal(out, a)


def test_apply_returns_float32(identity_ctl):
    a = np.array([[0.5, 0.5, 0.5]], dtype=np.float32)
    out = _ctl_native.apply(a, [str(identity_ctl)], {})
    assert out.dtype == np.float32
    assert out.shape == (1, 3)


def test_apply_1d_to_n3(identity_ctl):
    a = np.array([0.0, 0.18, 0.5, 1.0], dtype=np.float32)
    out = ctl.apply(a, identity_ctl)
    assert out.shape == (4, 3)
    assert np.all(out[:, 0] == out[:, 1])
    assert np.all(out[:, 1] == out[:, 2])


def test_apply_image_hwc(scale2x_ctl):
    img = np.full((4, 5, 3), 0.25, dtype=np.float32)
    out = ctl.apply(img, scale2x_ctl)
    assert out.shape == (4, 5, 3)
    np.testing.assert_array_almost_equal(out, np.full_like(img, 0.5))


def test_apply_single_triplet(identity_ctl):
    a = np.array([0.1, 0.2, 0.3], dtype=np.float32)
    out = ctl.apply(a, identity_ctl)
    assert out.shape == (3,)
    np.testing.assert_array_almost_equal(out, a)


def test_apply_dtype_preserved(identity_ctl):
    a = np.array([0.5, 0.5, 0.5], dtype=np.float64)
    out = ctl.apply(a, identity_ctl)
    assert out.dtype == np.float64


def test_apply_rejects_4_channels(identity_ctl):
    a = np.zeros((4, 4), dtype=np.float32)
    with pytest.raises(ValueError, match="input must be"):
        ctl.apply(a, identity_ctl)


def test_apply_accepts_path_object(identity_ctl):
    a = np.array([[0.5, 0.5, 0.5]], dtype=np.float32)
    out = ctl.apply(a, identity_ctl)  # identity_ctl is a Path
    assert out.shape == (1, 3)
