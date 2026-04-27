import os
import signal
import threading
import time

import numpy as np
import pytest

import ctl


@pytest.mark.skipif(os.name == "nt", reason="signal semantics differ on Windows")
def test_keyboard_interrupt(scale2x_ctl):
    """Ctrl+C (SIGINT) sent mid-compute should raise KeyboardInterrupt, not hang."""
    img = np.random.rand(4096, 4096, 3).astype(np.float32)
    ctl.apply(img[:1, :1, :], scale2x_ctl)  # warm cache

    def fire():
        time.sleep(0.05)
        os.kill(os.getpid(), signal.SIGINT)

    t = threading.Thread(target=fire, daemon=True)
    t.start()
    # Loop many times so the SIGINT lands inside the parallel compute window.
    with pytest.raises(KeyboardInterrupt):  # noqa: PT012
        for _ in range(50):
            ctl.apply(img, scale2x_ctl)
    t.join()
