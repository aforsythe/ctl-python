# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Alex Forsythe, Academy of Motion Picture Arts and Sciences

include_guard(GLOBAL)
include(FetchContent)

option(CTL_FETCH "Fetch and build CTL from source" ON)
set(CTL_SOURCE_DIR "" CACHE PATH "Path to CTL source checkout (overrides CTL_FETCH)")
set(CTL_BUILD_DIR  "" CACHE PATH "Path to CTL build dir (sibling to CTL_SOURCE_DIR)")

if(CTL_SOURCE_DIR AND CTL_BUILD_DIR)
    message(STATUS "Using developer CTL: ${CTL_SOURCE_DIR}")
    add_library(CTL::IlmCtl     STATIC IMPORTED GLOBAL)
    add_library(CTL::IlmCtlSimd STATIC IMPORTED GLOBAL)
    add_library(CTL::IlmCtlMath STATIC IMPORTED GLOBAL)
    set_target_properties(CTL::IlmCtl     PROPERTIES IMPORTED_LOCATION
        "${CTL_BUILD_DIR}/lib/IlmCtl/libIlmCtl.a"
        INTERFACE_INCLUDE_DIRECTORIES "${CTL_SOURCE_DIR}/lib/IlmCtl")
    set_target_properties(CTL::IlmCtlSimd PROPERTIES IMPORTED_LOCATION
        "${CTL_BUILD_DIR}/lib/IlmCtlSimd/libIlmCtlSimd.a"
        INTERFACE_INCLUDE_DIRECTORIES "${CTL_SOURCE_DIR}/lib/IlmCtlSimd")
    set_target_properties(CTL::IlmCtlMath PROPERTIES IMPORTED_LOCATION
        "${CTL_BUILD_DIR}/lib/IlmCtlMath/libIlmCtlMath.a"
        INTERFACE_INCLUDE_DIRECTORIES "${CTL_SOURCE_DIR}/lib/IlmCtlMath")
    find_package(Imath CONFIG REQUIRED)
    find_package(OpenEXR CONFIG REQUIRED)
elseif(CTL_FETCH)
    message(STATUS "Fetching CTL ctl-1.5.5 via FetchContent")
    FetchContent_Declare(ctl
        GIT_REPOSITORY https://github.com/aces-aswf/CTL.git
        GIT_TAG        ctl-1.5.5
        GIT_SHALLOW    TRUE
    )
    set(CTL_BUILD_TESTS OFF CACHE BOOL "" FORCE)
    set(CTL_BUILD_TOOLS OFF CACHE BOOL "" FORCE)
    set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
    FetchContent_MakeAvailable(ctl)
    add_library(CTL::IlmCtl     ALIAS IlmCtl)
    add_library(CTL::IlmCtlSimd ALIAS IlmCtlSimd)
    add_library(CTL::IlmCtlMath ALIAS IlmCtlMath)
    find_package(Imath CONFIG REQUIRED)
    find_package(OpenEXR CONFIG REQUIRED)
else()
    message(FATAL_ERROR "Set CTL_FETCH=ON or provide CTL_SOURCE_DIR + CTL_BUILD_DIR.")
endif()
