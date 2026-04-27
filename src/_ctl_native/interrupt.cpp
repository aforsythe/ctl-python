// SPDX-License-Identifier: Apache-2.0
// Copyright (c) 2026 Alex Forsythe, Academy of Motion Picture Arts and Sciences
#include "interrupt.hpp"
#include <pybind11/pybind11.h>

namespace ctlpython {

void check_interrupt() {
    pybind11::gil_scoped_acquire g;
    if (PyErr_CheckSignals() != 0) {
        throw pybind11::error_already_set();
    }
}

}
