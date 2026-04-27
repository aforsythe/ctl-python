// SPDX-License-Identifier: Apache-2.0
// Copyright (c) 2026 Alex Forsythe, Academy of Motion Picture Arts and Sciences
#pragma once
#include "overrides.hpp"
#include <CtlSimdInterpreter.h>
#include <CtlFunctionCall.h>
#include <unordered_map>
#include <string>
#include <optional>

namespace ctlpython {

// Run a single CTL transform across a multi-thread tile dispatch.
// Inputs: contiguous float arrays for R/G/B, length numSamples.
// Outputs: contiguous float arrays for R/G/B, length numSamples (caller-allocated).
// All newFunctionCall() calls happen on the calling thread before worker threads
// are spawned; CTL's newFunctionCall holds its own internal mutex but we keep
// it single-threaded for safety and to avoid contention.
void run_parallel_transform(
    Ctl::SimdInterpreter& interp,
    size_t numSamples,
    const float* in_r, const float* in_g, const float* in_b,
    float* out_r, float* out_g, float* out_b,
    const std::unordered_map<std::string, ScalarValue>& scalar_overrides,
    const std::unordered_map<std::string, double>& varying_overrides,
    std::optional<float> default_alpha
);

}
