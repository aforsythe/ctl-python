// SPDX-License-Identifier: Apache-2.0
// Copyright (c) 2026 Alex Forsythe, Academy of Motion Picture Arts and Sciences
#include "overrides.hpp"
#include "exceptions.hpp"
#include "levenshtein.hpp"
#include <CtlSimdInterpreter.h>
#include <CtlType.h>
#include <algorithm>
#include <cstring>
#include <sstream>
#include <stdexcept>
#include <vector>

namespace ctlpython {

static void write_scalar_uniform(Ctl::FunctionArg& p, const ScalarValue& v) {
    const std::string t = p.type()->asString();
    if (t == "float") {
        float f = v.tag == ScalarValue::F ? float(v.f)
                : v.tag == ScalarValue::I ? float(v.i)
                                          : float(v.b ? 1.0f : 0.0f);
        std::memcpy(p.data(), &f, sizeof(f));
    } else if (t == "int") {
        int i = v.tag == ScalarValue::I ? int(v.i)
              : v.tag == ScalarValue::F ? int(v.f)
                                        : int(v.b);
        std::memcpy(p.data(), &i, sizeof(i));
    } else if (t == "unsigned int") {
        unsigned int u = v.tag == ScalarValue::I ? static_cast<unsigned int>(v.i)
                       : v.tag == ScalarValue::F ? static_cast<unsigned int>(v.f)
                                                 : static_cast<unsigned int>(v.b);
        std::memcpy(p.data(), &u, sizeof(u));
    } else if (t == "bool") {
        char b = v.tag == ScalarValue::B ? char(v.b)
                                          : char(v.tag == ScalarValue::F ? v.f != 0 : v.i != 0);
        std::memcpy(p.data(), &b, sizeof(b));
    } else {
        throw ParameterError(
            "override of CTL type '" + t + "' is not supported (only float/int/bool)");
    }
}

void bind_scalar_overrides(
    Ctl::FunctionCall& fn,
    const std::unordered_map<std::string, ScalarValue>& overrides
) {
    // First three inputs are bound to the input array's R/G/B channels.
    std::vector<std::string> channelNames;
    for (size_t i = 0; i < std::min<size_t>(3, fn.numInputArgs()); ++i)
        channelNames.push_back(fn.inputArg(i)->name());

    // Names that ARE overridable: every input arg after the first 3.
    std::vector<std::string> overridable;
    for (size_t i = 3; i < fn.numInputArgs(); ++i)
        overridable.push_back(fn.inputArg(i)->name());

    for (const auto& kv : overrides) {
        const std::string& name = kv.first;
        const ScalarValue& val  = kv.second;

        // Channel collision check
        for (const auto& ch : channelNames) {
            if (name == ch) {
                throw ParameterError(
                    "'" + name + "' is bound to the input array's R/G/B channel and cannot be overridden");
            }
        }

        // Find param by name in inputs[3..]
        Ctl::FunctionArg* found = nullptr;
        for (size_t i = 3; i < fn.numInputArgs(); ++i) {
            if (fn.inputArg(i)->name() == name) {
                found = fn.inputArg(i).pointer();
                break;
            }
        }

        if (!found) {
            std::string hint = nearest_word(name, overridable);
            std::ostringstream msg;
            msg << "no CTL input named '" << name << "'";
            if (!hint.empty()) msg << " (did you mean '" << hint << "'?)";
            throw ParameterError(msg.str());
        }

        if (found->isVarying()) {
            // Varying overrides are handled per-chunk in apply_varying_broadcasts.
            // Only float varying broadcasts are supported; validate type here.
            const std::string t = found->type()->asString();
            if (t != "float") {
                throw ParameterError(
                    "varying override of CTL type '" + t + "' is not supported (only float)");
            }
            continue;
        }

        // Uniform override: write the scalar.
        write_scalar_uniform(*found, val);
    }

    // Verify every non-channel uniform input has either an override or a default.
    // CTL's SimdFunctionArg holds the default in a separate _defaultReg; the
    // live _reg is zero-initialised. setDefaultValue() copies the default into
    // _reg so callFunction() reads the right value. Without this call, defaulted
    // params silently produce zero output.
    for (size_t i = 3; i < fn.numInputArgs(); ++i) {
        Ctl::FunctionArg* p = fn.inputArg(i).pointer();
        if (p->isVarying()) continue;
        if (overrides.count(p->name())) continue;
        if (!p->hasDefaultValue()) {
            throw ParameterError(
                "missing required CTL input '" + std::string(p->name()) +
                "' (no default; pass as keyword)");
        }
        p->setDefaultValue();
    }
}

std::unordered_map<std::string, double> extract_varying_overrides(
    Ctl::FunctionCall& fn,
    const std::unordered_map<std::string, ScalarValue>& overrides
) {
    std::unordered_map<std::string, double> result;
    for (const auto& kv : overrides) {
        const std::string& name = kv.first;
        const ScalarValue& val  = kv.second;

        // Find the arg among inputs[3..]; skip if not found (already caught by bind_scalar_overrides)
        for (size_t i = 3; i < fn.numInputArgs(); ++i) {
            Ctl::FunctionArg* p = fn.inputArg(i).pointer();
            if (p->name() != name) continue;
            if (!p->isVarying()) break; // uniform; handled by bind_scalar_overrides

            // Already validated as float in bind_scalar_overrides; just extract value.
            double d = val.tag == ScalarValue::F ? val.f
                     : val.tag == ScalarValue::I ? double(val.i)
                                                 : double(val.b ? 1.0 : 0.0);
            result.emplace(name, d);
            break;
        }
    }
    return result;
}

void apply_varying_broadcasts(
    Ctl::FunctionCall& fn,
    size_t n,
    const std::unordered_map<std::string, double>& varying_scalars,
    std::optional<float> default_alpha
) {
    for (size_t i = 3; i < fn.numInputArgs(); ++i) {
        Ctl::FunctionArg* p = fn.inputArg(i).pointer();
        if (!p->isVarying()) continue;
        // Only float varying broadcasts are supported.
        if (p->type()->asString() != "float") continue;

        // Ensure the varying buffer is active before writing.
        p->setVarying(true);
        auto* data = reinterpret_cast<float*>(p->data());

        auto it = varying_scalars.find(p->name());
        if (it != varying_scalars.end()) {
            std::fill_n(data, n, static_cast<float>(it->second));
        } else if (default_alpha.has_value()
                   && std::string(p->name()) == "aIn"
                   && !p->hasDefaultValue()) {
            std::fill_n(data, n, *default_alpha);
        }
        // else: no override and not aIn auto-default. CTL does not auto-apply
        // varying defaults; setDefaultValue() would be needed to support that.
    }
}

void validate_varying_required(
    Ctl::FunctionCall& fn,
    const std::unordered_map<std::string, ScalarValue>& overrides,
    std::optional<float> default_alpha
) {
    for (size_t i = 3; i < fn.numInputArgs(); ++i) {
        Ctl::FunctionArg* p = fn.inputArg(i).pointer();
        if (!p->isVarying()) continue;
        if (p->type()->asString() != "float") continue;
        if (p->hasDefaultValue()) continue;
        if (overrides.count(p->name())) continue;
        const std::string name = p->name();
        if (default_alpha.has_value() && name == "aIn") continue;
        throw ParameterError(
            "missing required CTL input '" + name +
            "' (varying float; pass as keyword)");
    }
}

}
