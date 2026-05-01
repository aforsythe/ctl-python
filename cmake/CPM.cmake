# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Alex Forsythe, Academy of Motion Picture Arts and Sciences

set(CPM_DOWNLOAD_VERSION "0.40.8" CACHE STRING "CPM.cmake version to bootstrap")
set(CPM_DOWNLOAD_LOCATION "${CMAKE_BINARY_DIR}/cmake/CPM_${CPM_DOWNLOAD_VERSION}.cmake")

if(NOT EXISTS "${CPM_DOWNLOAD_LOCATION}")
    file(DOWNLOAD
        "https://github.com/cpm-cmake/CPM.cmake/releases/download/v${CPM_DOWNLOAD_VERSION}/CPM.cmake"
        "${CPM_DOWNLOAD_LOCATION}"
        TLS_VERIFY ON
        EXPECTED_HASH SHA256=78ba32abdf798bc616bab7c73aac32a17bbd7b06ad9e26a6add69de8f3ae4791
        STATUS DOWNLOAD_STATUS
        LOG DOWNLOAD_LOG
    )
    
    list(GET DOWNLOAD_STATUS 0 DOWNLOAD_CODE)
    list(GET DOWNLOAD_STATUS 1 DOWNLOAD_MESSAGE)
    
    if(NOT DOWNLOAD_CODE EQUAL 0)
        message(FATAL_ERROR "Failed to download CPM.cmake v${CPM_DOWNLOAD_VERSION}: ${DOWNLOAD_MESSAGE}")
    endif()
endif()

include("${CPM_DOWNLOAD_LOCATION}")
