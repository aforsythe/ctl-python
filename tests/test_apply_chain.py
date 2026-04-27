# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Alex Forsythe, Academy of Motion Picture Arts and Sciences
import numpy as np
import pytest

import ctl


def test_chain_two_scale2x(scale2x_ctl):
    a = np.array([0.1, 0.2, 0.3], dtype=np.float32)
    out = ctl.apply(a, [scale2x_ctl, scale2x_ctl])
    np.testing.assert_array_almost_equal(out, a * 4)


def test_chain_identity_then_scale(identity_ctl, scale2x_ctl):
    a = np.array([[0.25, 0.25, 0.25]], dtype=np.float32)
    out = ctl.apply(a, [identity_ctl, scale2x_ctl])
    np.testing.assert_array_almost_equal(out, [[0.5, 0.5, 0.5]])


def test_empty_chain_raises(identity_ctl):
    a = np.array([0.5, 0.5, 0.5], dtype=np.float32)
    with pytest.raises(ValueError, match="empty"):
        ctl.apply(a, [])
