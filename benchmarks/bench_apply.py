"""Compare in-process ctl.apply vs ctlrender subprocess across image sizes.

Run with::

    pytest benchmarks/bench_apply.py --benchmark-only \\
        --benchmark-columns=mean,stddev,rounds

Each benchmark is parameterised by a square image size. Both the in-process
binding and ctlrender are exercised on identical pixel data. The ctlrender
benchmarks are skipped if the CLI or the OpenEXR Python bindings are
unavailable.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from _ctlrender_helper import have_ctlrender, run_ctlrender

import ctl

FIX = Path(__file__).parent.parent / "tests" / "fixtures"
SCALE2X = FIX / "scale2x.ctl"

SIZES = [64, 256, 512, 1024, 2048]


@pytest.fixture(scope="module")
def warmed():
    """Warm the interpreter cache once for the whole module."""
    ctl.apply(np.zeros((1, 1, 3), dtype=np.float32), SCALE2X)


@pytest.mark.benchmark(group="in-process")
@pytest.mark.parametrize("n", SIZES)
def test_bench_in_process(benchmark, warmed, n):
    img = np.random.RandomState(n).rand(n, n, 3).astype(np.float32)
    benchmark(lambda: ctl.apply(img, SCALE2X))


@pytest.mark.skipif(not have_ctlrender(), reason="ctlrender unavailable")
@pytest.mark.benchmark(group="ctlrender")
@pytest.mark.parametrize("n", SIZES)
def test_bench_ctlrender(benchmark, n):
    img = np.random.RandomState(n).rand(n, n, 3).astype(np.float32)
    benchmark(lambda: run_ctlrender(img, [str(SCALE2X)]))
