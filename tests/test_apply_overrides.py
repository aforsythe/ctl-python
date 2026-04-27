import numpy as np
import pytest

import ctl
from ctl import CtlParameterError


def test_override_required_uniform_scalar(required_param_ctl):
    a = np.array([[0.25, 0.5, 0.75]], dtype=np.float32)
    out = ctl.apply(a, required_param_ctl, scale=4.0)
    np.testing.assert_array_almost_equal(out, [[1.0, 2.0, 3.0]])


def test_missing_required_param_raises(required_param_ctl):
    a = np.array([[0.5, 0.5, 0.5]], dtype=np.float32)
    with pytest.raises(CtlParameterError):
        ctl.apply(a, required_param_ctl)


def test_override_unknown_name_raises(identity_ctl):
    a = np.array([[0.5, 0.5, 0.5]], dtype=np.float32)
    with pytest.raises(CtlParameterError):
        ctl.apply(a, identity_ctl, no_such_param=1.0)


def test_override_collides_with_input_channel_raises(identity_ctl):
    a = np.array([[0.5, 0.5, 0.5]], dtype=np.float32)
    with pytest.raises(CtlParameterError):
        ctl.apply(a, identity_ctl, rIn=0.1)


def test_defaulted_uniform_uses_default(defaulted_param_ctl):
    a = np.array([[0.25, 0.5, 0.75]], dtype=np.float32)
    out = ctl.apply(a, defaulted_param_ctl)
    np.testing.assert_array_almost_equal(out, a * 2)


def test_defaulted_uniform_can_be_overridden(defaulted_param_ctl):
    a = np.array([[0.25, 0.5, 0.75]], dtype=np.float32)
    out = ctl.apply(a, defaulted_param_ctl, scale=10.0)
    np.testing.assert_array_almost_equal(out, a * 10)


def test_alpha_in_auto_defaults_to_one(alpha_passthrough_ctl):
    """aIn varying with no default should auto-broadcast to 1.0 (ACES convention)."""
    a = np.array([[0.5, 0.5, 0.5]], dtype=np.float32)
    out = ctl.apply(a, alpha_passthrough_ctl)
    np.testing.assert_array_almost_equal(out, a)


def test_alpha_in_can_be_overridden_scalar(alpha_passthrough_ctl):
    a = np.array([[0.5, 0.5, 0.5]], dtype=np.float32)
    out = ctl.apply(a, alpha_passthrough_ctl, aIn=0.25)
    np.testing.assert_array_almost_equal(out, a)


def test_alpha_into_red_auto_defaults_to_one(alpha_into_red_ctl):
    """Visible test of aIn auto-default: aIn flows into rOut, expected 1.0."""
    a = np.array([[0.3, 0.5, 0.7]], dtype=np.float32)
    out = ctl.apply(a, alpha_into_red_ctl)
    np.testing.assert_array_almost_equal(out, [[1.0, 0.5, 0.7]])


def test_alpha_into_red_override_visible(alpha_into_red_ctl):
    """Override aIn=0.25 must appear in rOut."""
    a = np.array([[0.3, 0.5, 0.7]], dtype=np.float32)
    out = ctl.apply(a, alpha_into_red_ctl, aIn=0.25)
    np.testing.assert_array_almost_equal(out, [[0.25, 0.5, 0.7]])


def test_default_alpha_disabled_raises(alpha_passthrough_ctl):
    """default_alpha=None disables auto-fill; missing aIn must raise."""
    a = np.array([[0.5, 0.5, 0.5]], dtype=np.float32)
    with pytest.raises(CtlParameterError):
        ctl.apply(a, alpha_passthrough_ctl, default_alpha=None)


def test_default_alpha_custom_value(alpha_into_red_ctl):
    """default_alpha=0.5 broadcasts 0.5 instead of the ACES default 1.0."""
    a = np.array([[0.3, 0.5, 0.7]], dtype=np.float32)
    out = ctl.apply(a, alpha_into_red_ctl, default_alpha=0.5)
    np.testing.assert_array_almost_equal(out, [[0.5, 0.5, 0.7]])


def test_default_alpha_disabled_with_explicit_override(alpha_into_red_ctl):
    """default_alpha=None still allows explicit aIn override."""
    a = np.array([[0.3, 0.5, 0.7]], dtype=np.float32)
    out = ctl.apply(a, alpha_into_red_ctl, aIn=0.4, default_alpha=None)
    np.testing.assert_array_almost_equal(out, [[0.4, 0.5, 0.7]])
