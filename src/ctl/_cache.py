"""Cache diagnostic API."""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from os import PathLike
from pathlib import Path

from ctl import _ctl_native


@dataclass(frozen=True)
class CacheEntry:
    path: str
    mtime_ns: int


def cache_info() -> list[CacheEntry]:
    """List currently cached CTL interpreter entries."""
    return [CacheEntry(**e) for e in _ctl_native.cache_info()]


def cache_clear() -> None:
    """Drop all cached interpreters. Useful after editing imported CTL modules."""
    _ctl_native.cache_clear()


def set_module_paths(paths: Sequence[str | PathLike[str]]) -> None:
    """Set the CTL import search path. Replaces any prior call.

    Combined with the CTL_MODULE_PATH environment variable: user paths are
    searched first, then env paths. Cache entries are NOT invalidated by
    module-path changes; call cache_clear() to force reload.

    Note: changing os.environ["CTL_MODULE_PATH"] mid-session only affects
    CTL files loaded AFTER the change (on each cache miss).
    """
    _ctl_native.set_module_paths([str(Path(p)) for p in paths])
