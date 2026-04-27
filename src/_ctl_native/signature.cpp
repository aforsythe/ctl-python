// SPDX-License-Identifier: Apache-2.0
// Copyright (c) 2026 Alex Forsythe, Academy of Motion Picture Arts and Sciences
#include "signature.hpp"
#include "exceptions.hpp"
#include <CtlSimdInterpreter.h>
#include <CtlFunctionCall.h>
#include <Iex.h>
#include <filesystem>

namespace py = pybind11;

static py::dict describe_input_arg(const Ctl::FunctionArgPtr& arg) {
    py::dict d;
    d["name"]        = arg->name();
    d["type"]        = arg->type()->asString();
    d["varying"]     = arg->isVarying();
    d["has_default"] = arg->hasDefaultValue();
    return d;
}

static py::dict describe_output_arg(const Ctl::FunctionArgPtr& arg) {
    py::dict d;
    d["name"]        = arg->name();
    d["type"]        = arg->type()->asString();
    d["varying"]     = arg->isVarying();
    d["has_default"] = false;  // outputs never have defaults
    return d;
}

static py::dict signature_impl(const std::string& path) {
    std::string abspath;
    try {
        abspath = std::filesystem::absolute(path).string();
    } catch (const std::filesystem::filesystem_error& e) {
        throw ctlpython::ParseError(std::string("path resolution failed: ") + e.what());
    }
    Ctl::SimdInterpreter interp;
    try {
        interp.loadFile(abspath);
    } catch (const Iex::BaseExc& e) {
        throw ctlpython::ParseError(std::string("CTL parse error: ") + e.what());
    }
    Ctl::FunctionCallPtr fn = interp.newFunctionCall("main");

    py::list inputs, outputs;
    for (size_t i = 0; i < fn->numInputArgs(); ++i)
        inputs.append(describe_input_arg(fn->inputArg(i)));
    for (size_t i = 0; i < fn->numOutputArgs(); ++i)
        outputs.append(describe_output_arg(fn->outputArg(i)));

    py::dict out;
    out["inputs"]  = inputs;
    out["outputs"] = outputs;
    out["path"]    = abspath;
    return out;
}

void register_signature(pybind11::module_& m) {
    m.def("signature", &signature_impl, py::arg("path"),
          "Return the main() signature of a CTL module as a dict.");
}
