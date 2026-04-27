from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"

@pytest.fixture
def identity_ctl() -> Path:
    return FIXTURES / "identity.ctl"

@pytest.fixture
def required_param_ctl() -> Path:
    return FIXTURES / "required_param.ctl"

@pytest.fixture
def scale2x_ctl() -> Path:
    return FIXTURES / "scale2x.ctl"

@pytest.fixture
def defaulted_param_ctl() -> Path:
    return FIXTURES / "defaulted_param.ctl"

@pytest.fixture
def alpha_passthrough_ctl() -> Path:
    return FIXTURES / "alpha_passthrough.ctl"

@pytest.fixture
def alpha_into_red_ctl() -> Path:
    return FIXTURES / "alpha_into_red.ctl"
