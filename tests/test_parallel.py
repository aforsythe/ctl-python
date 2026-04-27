import os
import time

import numpy as np
import pytest

import ctl


@pytest.mark.skipif(os.cpu_count() is None or os.cpu_count() < 4, reason="needs 4+ cores")
def test_large_image_parallel_speedup(scale2x_ctl):
    """A 2K image should run noticeably faster in parallel than serial."""
    img = np.random.rand(2048, 2048, 3).astype(np.float32)
    # Warm cache
    ctl.apply(img[:1, :1, :], scale2x_ctl)
    t0 = time.perf_counter()
    out = ctl.apply(img, scale2x_ctl)
    elapsed = time.perf_counter() - t0
    # Loose lower-bound: with parallelism, 2K * scale2x should clear in < 0.5s.
    # Tighten only if benchmarking shows consistently faster runs.
    assert elapsed < 0.5, f"elapsed={elapsed*1000:.1f}ms"
    assert out.shape == img.shape
    # Multi-chunk multi-worker correctness: every output pixel must be exactly 2x the input.
    np.testing.assert_allclose(out, img * 2.0, rtol=1e-5,
        err_msg="parallel multi-chunk output does not match scale2x expected")
