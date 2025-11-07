cmake_minimum_required(VERSION 3.15...3.27)

project(
  gwframe
  VERSION 0.1.0
  DESCRIPTION "Simplified Python bindings for LDASTools frameCPP"
  LANGUAGES CXX
)

# ==============================================================================
# Build Options
# ==============================================================================

option(USE_SYSTEM_FRAMECPP "Use system-installed frameCPP library" ON)

# Set C++ standard globally (required for nanobind)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# ==============================================================================
# Find Dependencies
# ==============================================================================

# Python and nanobind
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)

# Locate nanobind using Python (works in scikit-build-core's isolated environment)
execute_process(
  COMMAND "${Python_EXECUTABLE}" -m nanobind --cmake_dir
  OUTPUT_VARIABLE nanobind_ROOT
  OUTPUT_STRIP_TRAILING_WHITESPACE
  COMMAND_ERROR_IS_FATAL ANY
)
list(APPEND CMAKE_PREFIX_PATH "${nanobind_ROOT}")

find_package(nanobind CONFIG REQUIRED)

# frameCPP
if(USE_SYSTEM_FRAMECPP)
  find_package(PkgConfig REQUIRED)

  message(STATUS "Using system-installed frameCPP")
  pkg_check_modules(FRAMECPP REQUIRED framecpp)

  add_library(framecpp::framecpp INTERFACE IMPORTED)
  set_target_properties(framecpp::framecpp PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES "${FRAMECPP_INCLUDE_DIRS}"
    INTERFACE_LINK_LIBRARIES "${FRAMECPP_LINK_LIBRARIES}"
    INTERFACE_LINK_DIRECTORIES "${FRAMECPP_LIBRARY_DIRS}"
  )

  message(STATUS "  frameCPP version: ${FRAMECPP_VERSION}")
  message(STATUS "  Include dirs: ${FRAMECPP_INCLUDE_DIRS}")
  message(STATUS "  Library dirs: ${FRAMECPP_LIBRARY_DIRS}")

else()
  message(STATUS "Building frameCPP from source")

  set(FRAMECPP_SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/extern/framecpp")

  if(NOT EXISTS "${FRAMECPP_SOURCE_DIR}/CMakeLists.txt")
    message(FATAL_ERROR
      "frameCPP source not found at ${FRAMECPP_SOURCE_DIR}\n"
      "Either clone the source to extern/framecpp or use -DUSE_SYSTEM_FRAMECPP=ON"
    )
  endif()

  # frameCPP requires LDASToolsCMake and IGWNCMake modules
  # These can be provided via:
  #   - CMAKE_PREFIX_PATH environment/CMake variable
  #   - LDASToolsCMake_DIR and IGWNCMake_DIR CMake variables
  # Standard locations: <prefix>/share/{ldas-tools,igwn-cmake}/cmake/Modules

  # Configure frameCPP build
  set(BUILD_SHARED_LIBS OFF CACHE BOOL "Build static libraries" FORCE)
  set(BUILD_TESTING OFF CACHE BOOL "Disable tests" FORCE)
  set(ENABLE_DOCUMENTATION_ONLY OFF CACHE BOOL "Build full framecpp" FORCE)

  add_subdirectory(${FRAMECPP_SOURCE_DIR} extern/framecpp EXCLUDE_FROM_ALL)

  # Copy config header
  file(COPY "${CMAKE_CURRENT_BINARY_DIR}/extern/framecpp/framecpp_config.h"
       DESTINATION "${CMAKE_CURRENT_BINARY_DIR}")

  # Fix version library include paths
  foreach(version 3 4 6 7 8 9)
    if(TARGET framecpp${version})
      target_include_directories(framecpp${version} PRIVATE "${FRAMECPP_SOURCE_DIR}/src")
    endif()
  endforeach()

  # Create target alias
  if(TARGET framecpp9)
    add_library(framecpp::framecpp ALIAS framecpp9)
  else()
    message(FATAL_ERROR "framecpp9 target not found")
  endif()
endif()

# ==============================================================================
# Python Extension Module
# ==============================================================================

nanobind_add_module(
  _core
  NB_STATIC
  src/gwframe/_core.cpp
)

# Override nanobind's C++ standard (it defaults to C++14)
set_target_properties(_core PROPERTIES
  CXX_STANDARD 17
  CXX_STANDARD_REQUIRED ON
  CXX_EXTENSIONS OFF
)

target_link_libraries(_core PRIVATE framecpp::framecpp)

install(TARGETS _core LIBRARY DESTINATION gwframe)
