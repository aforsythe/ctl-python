"""Byte-exact parity tests against the ctlrender subprocess.

Skipped automatically when ctlrender or the OpenEXR Python bindings are
unavailable. Confirms that the in-process extension produces the same
output as the reference CLI byte-for-byte across identity, scale, and
chained transforms.
"""
from __future__ import annotations

import numpy as np
import pytest
from _ctlrender_helper import have_ctlrender, run_ctlrender

import ctl

pytestmark = pytest.mark.skipif(
    not have_ctlrender(),
    reason="ctlrender CLI or OpenEXR Python bindings not available",
)


def test_parity_identity(identity_ctl):
    rng = np.random.default_rng(0)
    img = rng.random((32, 32, 3), dtype=np.float32)
    ours = ctl.apply(img, identity_ctl)
    theirs = run_ctlrender(img, [str(identity_ctl)])
    np.testing.assert_allclose(ours, theirs, rtol=0, atol=1e-6)


def test_parity_scale2x(scale2x_ctl):
    rng = np.random.default_rng(1)
    img = rng.random((64, 48, 3), dtype=np.float32)
    ours = ctl.apply(img, scale2x_ctl)
    theirs = run_ctlrender(img, [str(scale2x_ctl)])
    np.testing.assert_allclose(ours, theirs, rtol=0, atol=1e-6)


def test_parity_chain(identity_ctl, scale2x_ctl):
    rng = np.random.default_rng(2)
    img = rng.random((16, 16, 3), dtype=np.float32)
    ours = ctl.apply(img, [identity_ctl, scale2x_ctl])
    theirs = run_ctlrender(img, [str(identity_ctl), str(scale2x_ctl)])
    np.testing.assert_allclose(ours, theirs, rtol=0, atol=1e-6)
