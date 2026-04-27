"""CTL signature introspection."""
from __future__ import annotations

from dataclasses import dataclass
from os import PathLike
from pathlib import Path

from ctl import _ctl_native
from ctl._errors import CtlParseError


@dataclass(frozen=True)
class CtlParam:
    name: str
    type: str
    varying: bool
    has_default: bool


@dataclass(frozen=True)
class CtlSignature:
    path: str
    inputs: tuple[CtlParam, ...]
    outputs: tuple[CtlParam, ...]

    def __str__(self) -> str:
        lines = [f"signature of {self.path}", "  inputs:"]
        for p in self.inputs:
            v = "varying" if p.varying else "uniform"
            d = "  (has default)" if p.has_default else ""
            lines.append(f"    {p.name:<18} {v:<8} {p.type}{d}")
        lines.append("  outputs:")
        for p in self.outputs:
            v = "varying" if p.varying else "uniform"
            lines.append(f"    {p.name:<18} {v:<8} {p.type}")
        return "\n".join(lines)


def signature(path: str | PathLike[str]) -> CtlSignature:
    """Return the declared `main()` signature of a CTL module."""
    try:
        raw = _ctl_native.signature(str(Path(path).resolve()))
    except _ctl_native._NativeParseError as exc:
        raise CtlParseError(str(exc)) from exc
    return CtlSignature(
        path=raw["path"],
        inputs=tuple(CtlParam(**p) for p in raw["inputs"]),
        outputs=tuple(CtlParam(**p) for p in raw["outputs"]),
    )
