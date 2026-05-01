# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Alex Forsythe, Academy of Motion Picture Arts and Sciences

include_guard(GLOBAL)
include(CPM)

option(CTL_FETCH "Fetch and build CTL from source when CTL_SOURCE_DIR is not set" ON)
set(CTL_SOURCE_DIR "" CACHE PATH "Path to CTL source checkout (overrides CTL_FETCH)")
set(CTL_BUILD_DIR "" CACHE PATH "Path to CTL build dir (used with CTL_SOURCE_DIR)")
set(_CTL_DEP_CTL_DEFAULT "1.5.5")
set(_CTL_DEP_IMATH_DEFAULT "3.1.11")
set(_CTL_DEP_OPENEXR_DEFAULT "3.2.9")
set(_CTL_DEP_LIBDEFLATE_DEFAULT "1.18")
set(_CTL_DEP_ZLIB_DEFAULT "1.3.1")

set(CTL_DEP_CTL "${_CTL_DEP_CTL_DEFAULT}" CACHE STRING "CTL version/tag, CPM URI, or source directory")
set(CTL_DEP_IMATH "${_CTL_DEP_IMATH_DEFAULT}" CACHE STRING "Imath version/tag, CPM URI, or source directory")
set(CTL_DEP_OPENEXR "${_CTL_DEP_OPENEXR_DEFAULT}" CACHE STRING "OpenEXR version/tag, CPM URI, or source directory")
set(CTL_DEP_LIBDEFLATE "${_CTL_DEP_LIBDEFLATE_DEFAULT}" CACHE STRING "libdeflate version/tag, CPM URI, or source directory")
set(CTL_DEP_ZLIB "${_CTL_DEP_ZLIB_DEFAULT}" CACHE STRING "zlib version/tag, CPM URI, or source directory")

function(_ctl_python_has_cpm_source_override package out_var)
    set(_source_var "CPM_${package}_SOURCE")
    if(DEFINED ${_source_var} AND NOT "${${_source_var}}" STREQUAL "")
        set(${out_var} TRUE PARENT_SCOPE)
    else()
        set(${out_var} FALSE PARENT_SCOPE)
    endif()
endfunction()

function(_ctl_python_cpm_args out_var package package_spec default_repo tag_prefix)
    if(IS_DIRECTORY "${package_spec}")
        set(_origin_args SOURCE_DIR "${package_spec}")
    elseif(package_spec MATCHES "^[a-zA-Z]+:")
        cpm_parse_add_package_single_arg("${package_spec}" _origin_args)
    else()
        if(package_spec MATCHES "^${tag_prefix}")
            set(_tag "${package_spec}")
            string(REGEX REPLACE "^${tag_prefix}" "" _version "${package_spec}")
        else()
            set(_version "${package_spec}")
            set(_tag "${tag_prefix}${package_spec}")
        endif()

        set(_origin_args
            GITHUB_REPOSITORY ${default_repo}
            VERSION ${_version}
            GIT_TAG ${_tag}
        )
    endif()

    set(${out_var}
        NAME ${package}
        ${_origin_args}
        PARENT_SCOPE
    )
endfunction()

function(_ctl_python_cpm_find_or_add package package_spec default_spec force_add)
    if(package_spec STREQUAL default_spec AND NOT force_add)
        CPMFindPackage(${ARGN})
    else()
        CPMAddPackage(${ARGN})
    endif()
endfunction()

function(_ctl_python_find_or_fetch_zlib)
    _ctl_python_has_cpm_source_override(ZLIB _has_source_override)
    if(TARGET ZLIB::ZLIB)
        return()
    endif()

    message(STATUS "Fetching zlib ${CTL_DEP_ZLIB} with CPM")
    set(ZLIB_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
    _ctl_python_cpm_args(_zlib_args ZLIB "${CTL_DEP_ZLIB}" "madler/zlib" "v")
    _ctl_python_cpm_find_or_add(ZLIB "${CTL_DEP_ZLIB}" "${_CTL_DEP_ZLIB_DEFAULT}" ${_has_source_override}
        ${_zlib_args}
        EXCLUDE_FROM_ALL YES
        SYSTEM YES
        OPTIONS "ZLIB_BUILD_EXAMPLES OFF"
    )

    if(TARGET zlibstatic AND NOT TARGET ZLIB::ZLIB)
        add_library(ZLIB::ZLIB ALIAS zlibstatic)
    elseif(TARGET zlib AND NOT TARGET ZLIB::ZLIB)
        add_library(ZLIB::ZLIB ALIAS zlib)
    endif()
endfunction()

function(_ctl_python_find_or_fetch_imath)
    _ctl_python_has_cpm_source_override(Imath _has_source_override)
    if(TARGET Imath::Imath)
        return()
    endif()

    message(STATUS "Fetching Imath ${CTL_DEP_IMATH} with CPM")
    set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
    set(BUILD_TESTING OFF CACHE BOOL "" FORCE)
    set(IMATH_INSTALL OFF CACHE BOOL "" FORCE)
    set(IMATH_INSTALL_PKG_CONFIG OFF CACHE BOOL "" FORCE)
    set(PYTHON OFF CACHE BOOL "" FORCE)
    _ctl_python_cpm_args(_imath_args Imath "${CTL_DEP_IMATH}" "AcademySoftwareFoundation/Imath" "v")
    _ctl_python_cpm_find_or_add(Imath "${CTL_DEP_IMATH}" "${_CTL_DEP_IMATH_DEFAULT}" ${_has_source_override}
        ${_imath_args}
        FIND_PACKAGE_ARGUMENTS CONFIG
        EXCLUDE_FROM_ALL YES
        SYSTEM YES
        OPTIONS
            "BUILD_TESTING OFF"
            "IMATH_INSTALL OFF"
            "IMATH_INSTALL_PKG_CONFIG OFF"
            "PYTHON OFF"
    )

    if(DEFINED Imath_BINARY_DIR AND EXISTS "${Imath_BINARY_DIR}/config/ImathConfig.cmake")
        set(Imath_DIR "${Imath_BINARY_DIR}/config" CACHE PATH "Path to fetched Imath config" FORCE)
    endif()
endfunction()

function(_ctl_python_find_or_fetch_libdeflate)
    _ctl_python_has_cpm_source_override(libdeflate _has_source_override)
    if(TARGET libdeflate::libdeflate_static OR TARGET libdeflate::libdeflate_shared)
        return()
    endif()

    message(STATUS "Fetching libdeflate ${CTL_DEP_LIBDEFLATE} with CPM")
    set(LIBDEFLATE_BUILD_GZIP OFF CACHE BOOL "" FORCE)
    set(LIBDEFLATE_BUILD_SHARED_LIB OFF CACHE BOOL "" FORCE)
    set(LIBDEFLATE_BUILD_STATIC_LIB ON CACHE BOOL "" FORCE)
    set(LIBDEFLATE_BUILD_TESTS OFF CACHE BOOL "" FORCE)
    _ctl_python_cpm_args(_libdeflate_args libdeflate "${CTL_DEP_LIBDEFLATE}" "ebiggers/libdeflate" "v")
    _ctl_python_cpm_find_or_add(libdeflate "${CTL_DEP_LIBDEFLATE}" "${_CTL_DEP_LIBDEFLATE_DEFAULT}" ${_has_source_override}
        ${_libdeflate_args}
        FIND_PACKAGE_ARGUMENTS CONFIG
        EXCLUDE_FROM_ALL YES
        SYSTEM YES
        OPTIONS
            "LIBDEFLATE_BUILD_GZIP OFF"
            "LIBDEFLATE_BUILD_SHARED_LIB OFF"
            "LIBDEFLATE_BUILD_STATIC_LIB ON"
            "LIBDEFLATE_BUILD_TESTS OFF"
    )

    if(DEFINED libdeflate_BINARY_DIR AND EXISTS "${libdeflate_BINARY_DIR}/libdeflate-config.cmake")
        set(libdeflate_DIR "${libdeflate_BINARY_DIR}" CACHE PATH "Path to fetched libdeflate config" FORCE)
    endif()
endfunction()

function(_ctl_python_find_or_fetch_openexr)
    _ctl_python_has_cpm_source_override(OpenEXR _has_source_override)
    if(OpenEXR_FOUND)
        find_package(Imath CONFIG QUIET)
        return()
    endif()

    message(STATUS "Fetching OpenEXR ${CTL_DEP_OPENEXR} with CPM")
    _ctl_python_find_or_fetch_imath()
    _ctl_python_find_or_fetch_libdeflate()

    set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
    set(BUILD_TESTING OFF CACHE BOOL "" FORCE)
    set(OPENEXR_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
    set(OPENEXR_BUILD_PYTHON OFF CACHE BOOL "" FORCE)
    set(OPENEXR_BUILD_TOOLS OFF CACHE BOOL "" FORCE)
    set(OPENEXR_INSTALL OFF CACHE BOOL "" FORCE)
    set(OPENEXR_INSTALL_DOCS OFF CACHE BOOL "" FORCE)
    set(OPENEXR_INSTALL_PKG_CONFIG OFF CACHE BOOL "" FORCE)
    set(OPENEXR_INSTALL_TOOLS OFF CACHE BOOL "" FORCE)
    set(OPENEXR_FORCE_INTERNAL_DEFLATE OFF CACHE BOOL "" FORCE)
    set(OPENEXR_FORCE_INTERNAL_IMATH OFF CACHE BOOL "" FORCE)
    if(NOT CTL_DEP_IMATH MATCHES "^[a-zA-Z]+:")
        if(CTL_DEP_IMATH MATCHES "^v")
            set(OPENEXR_IMATH_TAG "${CTL_DEP_IMATH}" CACHE STRING "" FORCE)
        else()
            set(OPENEXR_IMATH_TAG "v${CTL_DEP_IMATH}" CACHE STRING "" FORCE)
        endif()
    endif()

    _ctl_python_cpm_args(_openexr_args OpenEXR "${CTL_DEP_OPENEXR}" "AcademySoftwareFoundation/openexr" "v")
    _ctl_python_cpm_find_or_add(OpenEXR "${CTL_DEP_OPENEXR}" "${_CTL_DEP_OPENEXR_DEFAULT}" ${_has_source_override}
        ${_openexr_args}
        FIND_PACKAGE_ARGUMENTS CONFIG
        EXCLUDE_FROM_ALL YES
        SYSTEM YES
        OPTIONS
            "BUILD_TESTING OFF"
            "OPENEXR_BUILD_EXAMPLES OFF"
            "OPENEXR_BUILD_PYTHON OFF"
            "OPENEXR_BUILD_TOOLS OFF"
            "OPENEXR_INSTALL OFF"
            "OPENEXR_INSTALL_DOCS OFF"
            "OPENEXR_INSTALL_PKG_CONFIG OFF"
            "OPENEXR_INSTALL_TOOLS OFF"
            "OPENEXR_FORCE_INTERNAL_DEFLATE OFF"
            "OPENEXR_FORCE_INTERNAL_IMATH OFF"
    )

    if(DEFINED OpenEXR_BINARY_DIR AND EXISTS "${OpenEXR_BINARY_DIR}/cmake/OpenEXRConfig.cmake")
        set(OpenEXR_DIR "${OpenEXR_BINARY_DIR}/cmake" CACHE PATH "Path to fetched OpenEXR config" FORCE)
    endif()
    if(DEFINED imath_BINARY_DIR AND EXISTS "${imath_BINARY_DIR}/config/ImathConfig.cmake")
        set(Imath_DIR "${imath_BINARY_DIR}/config" CACHE PATH "Path to fetched Imath config" FORCE)
    endif()
endfunction()

_ctl_python_find_or_fetch_zlib()
_ctl_python_find_or_fetch_imath()
_ctl_python_find_or_fetch_openexr()

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
    find_package(OpenEXR 3 CONFIG REQUIRED)
elseif(CTL_FETCH)
    message(STATUS "Fetching CTL ${CTL_DEP_CTL} with CPM")
    set(CTL_BUILD_TESTS OFF CACHE BOOL "" FORCE)
    set(CTL_BUILD_TOOLS OFF CACHE BOOL "" FORCE)
    set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
    _ctl_python_cpm_args(_ctl_args ctl "${CTL_DEP_CTL}" "aces-aswf/CTL" "ctl-")
    CPMAddPackage(
        ${_ctl_args}
        EXCLUDE_FROM_ALL YES
        SYSTEM YES
        OPTIONS
            "CTL_BUILD_TESTS OFF"
            "CTL_BUILD_TOOLS OFF"
            "BUILD_SHARED_LIBS OFF"
    )
    add_library(CTL::IlmCtl     ALIAS IlmCtl)
    add_library(CTL::IlmCtlSimd ALIAS IlmCtlSimd)
    add_library(CTL::IlmCtlMath ALIAS IlmCtlMath)
    find_package(Imath CONFIG REQUIRED)
    find_package(OpenEXR CONFIG REQUIRED)
else()
    message(FATAL_ERROR "Set CTL_FETCH=ON or provide CTL_SOURCE_DIR + CTL_BUILD_DIR.")
endif()
