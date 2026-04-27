// SPDX-License-Identifier: Apache-2.0
// Copyright (c) 2026 Alex Forsythe, Academy of Motion Picture Arts and Sciences
#pragma once
#include <pybind11/pybind11.h>
#include <CtlSimdInterpreter.h>
#include <memory>
#include <string>
#include <unordered_map>
#include <chrono>
#include <vector>

namespace ctlpython {

struct CachedInterp {
    std::unique_ptr<Ctl::SimdInterpreter> interp;
    std::chrono::nanoseconds main_mtime;
    // List of (absolute_path, mtime) for all transitively imported .ctl files.
    // Any mtime change invalidates this cache entry. The import list is internal;
    // only main_mtime is exposed via info().
    std::vector<std::pair<std::string, std::chrono::nanoseconds>> imports;
    std::string path;
};

class InterpCache {
public:
    static InterpCache& instance();
    Ctl::SimdInterpreter& get_or_load(const std::string& path);
    pybind11::list info() const;
    void clear();
    void set_module_paths(std::vector<std::string> paths);
private:
    std::unordered_map<std::string, CachedInterp> map_;
    std::vector<std::string> user_paths_;
    static std::vector<std::string> env_paths();
};

}

void register_cache(pybind11::module_& m);
