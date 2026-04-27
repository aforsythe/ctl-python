import numpy as np
import pytest

import ctl
from ctl import CtlParameterError, CtlParseError


def test_invalid_ctl_path_raises_parse_error():
    a = np.array([[0.5, 0.5, 0.5]], dtype=np.float32)
    with pytest.raises(CtlParseError):
        ctl.apply(a, "/no/such/file.ctl")


def test_unknown_param_raises_parameter_error(identity_ctl):
    a = np.array([[0.5, 0.5, 0.5]], dtype=np.float32)
    with pytest.raises(CtlParameterError):
        ctl.apply(a, identity_ctl, no_such=1.0)


def test_signature_invalid_path_raises_parse_error():
    with pytest.raises(CtlParseError):
        ctl.signature("/no/such/file.ctl")
