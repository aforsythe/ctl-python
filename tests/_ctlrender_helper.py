"""Round-trip an array through the ctlrender CLI for parity testing."""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np

try:
    import OpenEXR
    HAS_EXR = True
except ImportError:
    HAS_EXR = False


def have_ctlrender() -> bool:
    return shutil.which("ctlrender") is not None and HAS_EXR


def _write_exr(path: Path, image: np.ndarray) -> None:
    """Write a (H, W, 3) float32 array to a 16-bit-or-32-bit-float EXR.

    Uses the OpenEXR 3.x ``File`` API.
    """
    if image.ndim != 3 or image.shape[-1] != 3:
        raise ValueError(f"expected (H,W,3), got {image.shape}")
    channels = {
        "R": image[..., 0].astype(np.float32),
        "G": image[..., 1].astype(np.float32),
        "B": image[..., 2].astype(np.float32),
    }
    header = {"compression": OpenEXR.ZIP_COMPRESSION, "type": OpenEXR.scanlineimage}
    with OpenEXR.File(header, channels) as f:
        f.write(str(path))


def _read_exr(path: Path) -> np.ndarray:
    """Read an EXR file into a (H, W, 3) float32 numpy array.

    OpenEXR may group R/G/B as a single multi-component channel ("RGB" with
    shape (H, W, 3)) or as three separate channels (R, G, B each (H, W)).
    Both layouts are handled; alpha is stripped if present.
    """
    with OpenEXR.File(str(path)) as f:
        parts = list(f.parts)
        if not parts:
            raise RuntimeError(f"no parts in {path}")
        ch = parts[0].channels
        # Grouped layout: a single channel of shape (H, W, 3+).
        if "RGB" in ch:
            arr = np.asarray(ch["RGB"].pixels)
            return arr[..., :3].astype(np.float32)
        if "RGBA" in ch:
            arr = np.asarray(ch["RGBA"].pixels)
            return arr[..., :3].astype(np.float32)
        # Per-channel layout.
        names = list(ch.keys())
        order = ["R", "G", "B"]
        if not all(n in names for n in order):
            order = names[:3]
        planes = [np.squeeze(np.asarray(ch[n].pixels)) for n in order]
        return np.stack(planes, axis=-1).astype(np.float32)


def run_ctlrender(image: np.ndarray, ctl_paths: list[str]) -> np.ndarray:
    """Apply CTL via subprocess. Image is (H, W, 3) float32. Returns same shape."""
    if image.ndim != 3 or image.shape[-1] != 3:
        raise ValueError("run_ctlrender expects (H, W, 3) input")
    with tempfile.TemporaryDirectory() as tmp:
        in_path = Path(tmp) / "in.exr"
        out_path = Path(tmp) / "out.exr"
        _write_exr(in_path, image.astype(np.float32, copy=False))
        cmd = ["ctlrender", "-force", "-format", "exr32"]
        for p in ctl_paths:
            cmd += ["-ctl", p]
        cmd += [str(in_path), str(out_path)]
        subprocess.run(cmd, check=True, capture_output=True)
        return _read_exr(out_path)
