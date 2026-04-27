"""CTL exception hierarchy."""
from __future__ import annotations


class CtlError(RuntimeError):
    """Base class for all CTL-related errors raised by this package."""


class CtlParseError(CtlError):
    """The CTL module failed to load or parse."""


class CtlRuntimeError(CtlError):
    """A CTL transform raised an exception during execution."""


class CtlParameterError(CtlError):
    """A user-supplied parameter override is invalid (unknown name, wrong type, collision)."""
