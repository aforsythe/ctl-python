# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Alex Forsythe, Academy of Motion Picture Arts and Sciences

cmake_minimum_required(VERSION 3.24)
project(ctl_python LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

if(APPLE AND NOT CMAKE_OSX_DEPLOYMENT_TARGET)
    set(CMAKE_OSX_DEPLOYMENT_TARGET "11.0" CACHE STRING "macOS deployment target")
endif()

list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")
include(FindOrFetchCTL)

set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 CONFIG REQUIRED)

set(NATIVE_SRC
    src/_ctl_native/module.cpp
    src/_ctl_native/apply.cpp
    src/_ctl_native/array_marshal.cpp
    src/_ctl_native/signature.cpp
    src/_ctl_native/cache.cpp
    src/_ctl_native/overrides.cpp
    src/_ctl_native/tiling.cpp
    src/_ctl_native/interrupt.cpp
)

pybind11_add_module(_ctl_native MODULE ${NATIVE_SRC})

target_link_libraries(_ctl_native PRIVATE
    CTL::IlmCtlSimd CTL::IlmCtlMath CTL::IlmCtl
    Imath::Imath OpenEXR::Iex
)

target_include_directories(_ctl_native PRIVATE src/_ctl_native)

if(APPLE)
    find_library(ACCELERATE_FRAMEWORK Accelerate)
    if(ACCELERATE_FRAMEWORK)
        target_link_libraries(_ctl_native PRIVATE ${ACCELERATE_FRAMEWORK})
    endif()
endif()

install(TARGETS _ctl_native LIBRARY DESTINATION ctl)
