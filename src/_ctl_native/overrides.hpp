// SPDX-License-Identifier: Apache-2.0
// Copyright (c) 2026 Alex Forsythe, Academy of Motion Picture Arts and Sciences
#pragma once
#include <CtlFunctionCall.h>
#include <optional>
#include <string>
#include <unordered_map>

namespace ctlpython {

struct ScalarValue {
    enum Tag { F, I, B } tag;
    double f = 0.0;
    long long i = 0;
    bool b = false;
};

// Apply uniform/scalar overrides. Throws std::invalid_argument with edit-distance
// hints on unknown names, channel collisions, missing required params.
// Varying overrides are validated for type but deferred to apply_varying_broadcasts.
void bind_scalar_overrides(
    Ctl::FunctionCall& fn,
    const std::unordered_map<std::string, ScalarValue>& overrides
);

// Extract user-provided overrides for varying float inputs[3..] into a plain
// double map. Throws if the user overrides a varying non-float param (unsupported).
// Uniform args and non-overridden args are skipped.
std::unordered_map<std::string, double> extract_varying_overrides(
    Ctl::FunctionCall& fn,
    const std::unordered_map<std::string, ScalarValue>& overrides
);

// Apply per-chunk broadcasts for varying inputs[3..]:
//  * If `name` is in `varying_scalars`, fill the buffer with that scalar.
//  * Else if `default_alpha` has a value and the arg is a varying float
//    named "aIn" with no default, fill with that value (ACES convention).
//  * Else leave the buffer alone.
void apply_varying_broadcasts(
    Ctl::FunctionCall& fn,
    size_t numSamples,
    const std::unordered_map<std::string, double>& varying_scalars,
    std::optional<float> default_alpha
);

// Validate that every varying float input[3..] without a CTL default has
// either a user override OR is `aIn` with `default_alpha` enabled. Throws
// std::invalid_argument otherwise. Pre-condition: bind_scalar_overrides
// already ran (uniform overrides written, channel collisions rejected).
void validate_varying_required(
    Ctl::FunctionCall& fn,
    const std::unordered_map<std::string, ScalarValue>& overrides,
    std::optional<float> default_alpha
);

}
