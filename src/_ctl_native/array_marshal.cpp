// SPDX-License-Identifier: Apache-2.0
// Copyright (c) 2026 Alex Forsythe, Academy of Motion Picture Arts and Sciences
#include "array_marshal.hpp"
#include <stdexcept>

namespace ctlpython {

Planes split_n3_to_planes(pybind11::array_t<float, pybind11::array::c_style | pybind11::array::forcecast> a) {
    auto buf = a.unchecked<2>();
    if (buf.shape(1) != 3) throw std::invalid_argument("expected (N, 3) array");
    Planes p;
    p.numSamples = static_cast<size_t>(buf.shape(0));
    p.r.resize(p.numSamples); p.g.resize(p.numSamples); p.b.resize(p.numSamples);
    for (size_t i = 0; i < p.numSamples; ++i) {
        p.r[i] = buf(i, 0);
        p.g[i] = buf(i, 1);
        p.b[i] = buf(i, 2);
    }
    return p;
}

pybind11::array_t<float> planes_to_n3(const Planes& p) {
    pybind11::array_t<float> out({p.numSamples, size_t(3)});
    auto m = out.mutable_unchecked<2>();
    for (size_t i = 0; i < p.numSamples; ++i) {
        m(i, 0) = p.r[i]; m(i, 1) = p.g[i]; m(i, 2) = p.b[i];
    }
    return out;
}

}
