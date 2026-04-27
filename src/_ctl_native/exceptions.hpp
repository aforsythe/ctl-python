// SPDX-License-Identifier: Apache-2.0
// Copyright (c) 2026 Alex Forsythe, Academy of Motion Picture Arts and Sciences
#pragma once
#include <stdexcept>

namespace ctlpython {

struct ParseError : public std::runtime_error {
    using std::runtime_error::runtime_error;
};

struct RuntimeErr : public std::runtime_error {
    using std::runtime_error::runtime_error;
};

struct ParameterError : public std::runtime_error {
    using std::runtime_error::runtime_error;
};

}
