// SPDX-License-Identifier: Apache-2.0
// Copyright (c) 2026 Alex Forsythe, Academy of Motion Picture Arts and Sciences
#pragma once
#include <pybind11/numpy.h>
#include <vector>

namespace ctlpython {

struct Planes {
    std::vector<float> r, g, b;   // length = numSamples
    size_t numSamples;
};

Planes split_n3_to_planes(pybind11::array_t<float, pybind11::array::c_style | pybind11::array::forcecast> a);
pybind11::array_t<float> planes_to_n3(const Planes& p);

}
