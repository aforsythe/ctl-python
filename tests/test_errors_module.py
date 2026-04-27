import pytest

from ctl import CtlError, CtlParameterError, CtlParseError, CtlRuntimeError


def test_error_hierarchy():
    assert issubclass(CtlParseError, CtlError)
    assert issubclass(CtlRuntimeError, CtlError)
    assert issubclass(CtlParameterError, CtlError)
    assert issubclass(CtlError, RuntimeError)


def test_error_can_be_raised():
    with pytest.raises(CtlError):
        raise CtlParseError("oops")
