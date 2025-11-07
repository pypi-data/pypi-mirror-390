#!/bin/bash
set -e  # Exit on error

# Fetch and build LDAS Tools dependencies for wheel building
# This script downloads and builds framecpp and its dependencies from software.igwn.org
# for creating self-contained Python wheels
# Based on conda-forge build configurations

# Determine the script directory at the start (before changing directories)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "Fetching LDAS Tools for framecpp build"
echo "=========================================="

# Configuration - stable release versions
# software.igwn.org has the latest versions, software.ligo.org has older releases
IGWN_CMAKE_VERSION="1.6.0"
IGWN_CMAKE_URL="http://software.igwn.org/sources/source"

LDAS_TOOLS_CMAKE_VERSION="1.3.1"
LDAS_TOOLS_CMAKE_URL="http://software.igwn.org/sources/source"

LDAS_TOOLS_AL_VERSION="2.7.0"
LDAS_TOOLS_AL_URL="http://software.igwn.org/sources/source"

LDAS_TOOLS_FRAMECPP_VERSION="2.9.3"
LDAS_TOOLS_FRAMECPP_URL="http://software.igwn.org/sources/source"
BUILD_DIR="${BUILD_DIR:-$(pwd)/ldas_build}"
INSTALL_PREFIX="${INSTALL_PREFIX:-$(pwd)/ldas_install}"

# Detect platform and set platform-specific flags (from conda-forge)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Link librt for clock_gettime on older glibc versions
    export LDFLAGS="-lrt ${LDFLAGS:-}"
    echo "Platform: Linux (adding -lrt to LDFLAGS)"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS-specific flags (following conda-forge best practices)
    echo "Platform: macOS"
    # Disable C++ availability checks for better compatibility across macOS versions
    # This prevents issues with std::filesystem and other modern C++ features
    export CXXFLAGS="${CXXFLAGS:-} -D_LIBCPP_DISABLE_AVAILABILITY"
    echo "  CXXFLAGS: $CXXFLAGS"
fi

# Common CMake flags (following conda-forge best practices)
# Note: Using Release instead of RelWithDebInfo to reduce library size
# (no debug symbols = smaller static libraries for wheels)
CMAKE_COMMON_FLAGS=(
    -DCMAKE_BUILD_TYPE=Release  # Fully optimized, no debug symbols
    -DCMAKE_POLICY_VERSION_MINIMUM=3.5  # Handle old CMake versions
    -DCMAKE_DISABLE_FIND_PACKAGE_Doxygen=true  # No documentation
)

# macOS-specific: Set target architecture for CMake library checks
# Based on conda-forge: https://github.com/conda-forge/ldas-tools-framecpp-feedstock/blob/main/recipe/build.sh
# This ensures CMake's check_library_exists() compiles test programs for the correct architecture
if [[ "$OSTYPE" == "darwin"* ]]; then
    OSX_ARCH=$(uname -m)
    CMAKE_COMMON_FLAGS+=(-DCMAKE_OSX_ARCHITECTURES="${OSX_ARCH}")
    echo "Setting CMAKE_OSX_ARCHITECTURES=${OSX_ARCH}"
fi

# Parallel build jobs
NPROC=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 2)

# Create build and install directories
mkdir -p "$BUILD_DIR"
mkdir -p "$INSTALL_PREFIX"

# Set PKG_CONFIG_PATH to find .pc files from our local install
# This allows later builds to find dependencies from earlier builds
export PKG_CONFIG_PATH="${INSTALL_PREFIX}/lib/pkgconfig:${INSTALL_PREFIX}/lib64/pkgconfig:${INSTALL_PREFIX}/share/pkgconfig${PKG_CONFIG_PATH:+:${PKG_CONFIG_PATH}}"
echo "PKG_CONFIG_PATH: $PKG_CONFIG_PATH"

cd "$BUILD_DIR"

# Helper function to download and extract tarball
fetch_and_extract() {
    local name=$1
    local version=$2
    local base_url=$3
    local tarball="${name}-${version}.tar.gz"
    local url="${base_url}/${tarball}"

    echo "Fetching ${name} ${version} from ${base_url}..."
    if [ ! -f "$tarball" ]; then
        if command -v wget &> /dev/null; then
            wget "$url" || { echo "Error: wget failed to download ${url}"; exit 1; }
        elif command -v curl &> /dev/null; then
            curl -LO "$url" || { echo "Error: curl failed to download ${url}"; exit 1; }
        else
            echo "Error: neither wget nor curl is available"
            exit 1
        fi
    fi

    echo "Extracting ${tarball}..."
    tar -xzf "$tarball" || { echo "Error: failed to extract ${tarball}"; exit 1; }

    # Verify the extracted directory exists
    local expected_dir="${name}-${version}"
    if [ ! -d "$expected_dir" ]; then
        echo "Error: expected directory ${expected_dir} not found after extraction"
        ls -la
        exit 1
    fi
}

# Build order (dependencies first):
# 1. igwn-cmake-macros - CMake modules
# 2. ldas-tools-cmake - LDAS Tools CMake modules
# 3. ldas-tools-al - Abstract layer library
# 4. ldas-tools-framecpp - Frame library

echo ""
echo "=========================================="
echo "1/4: Fetching and building igwn-cmake-macros ${IGWN_CMAKE_VERSION}"
echo "=========================================="
fetch_and_extract "igwn-cmake-macros" "$IGWN_CMAKE_VERSION" "$IGWN_CMAKE_URL"
cd "$BUILD_DIR/igwn-cmake-macros-${IGWN_CMAKE_VERSION}"
mkdir -p build && cd build
cmake .. \
    "${CMAKE_COMMON_FLAGS[@]}" \
    -DCMAKE_INSTALL_PREFIX="$INSTALL_PREFIX"
cmake --build . --parallel "$NPROC"
cmake --install .

echo ""
echo "=========================================="
echo "2/4: Fetching and building ldas-tools-cmake ${LDAS_TOOLS_CMAKE_VERSION}"
echo "=========================================="
cd "$BUILD_DIR"
fetch_and_extract "ldas-tools-cmake" "$LDAS_TOOLS_CMAKE_VERSION" "$LDAS_TOOLS_CMAKE_URL"
cd "$BUILD_DIR/ldas-tools-cmake-${LDAS_TOOLS_CMAKE_VERSION}"
mkdir -p build && cd build
# Preserve environment CMAKE_PREFIX_PATH (from CI) and prepend our install prefix
# This ensures CMake can find system dependencies (OpenSSL, Boost) from /opt/local
# while also finding our locally built dependencies
COMBINED_PREFIX_PATH="$INSTALL_PREFIX${CMAKE_PREFIX_PATH:+:${CMAKE_PREFIX_PATH}}"
echo "CMAKE_PREFIX_PATH: $COMBINED_PREFIX_PATH"
cmake .. \
    "${CMAKE_COMMON_FLAGS[@]}" \
    -DCMAKE_INSTALL_PREFIX="$INSTALL_PREFIX" \
    -DCMAKE_PREFIX_PATH="$COMBINED_PREFIX_PATH"
cmake --build . --parallel "$NPROC"
cmake --install .

echo ""
echo "=========================================="
echo "3/4: Fetching and building ldas-tools-al ${LDAS_TOOLS_AL_VERSION}"
echo "=========================================="
cd "$BUILD_DIR"
fetch_and_extract "ldas-tools-al" "$LDAS_TOOLS_AL_VERSION" "$LDAS_TOOLS_AL_URL"
cd "$BUILD_DIR/ldas-tools-al-${LDAS_TOOLS_AL_VERSION}"

# Apply macOS patches from conda-forge (stored locally in tools/patches/)
# https://github.com/conda-forge/ldas-tools-al-feedstock/tree/main/recipe
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Applying macOS patches for ldas-tools-al..."

    PATCHES_DIR="${SCRIPT_DIR}/patches"

    # Patch 1: Remove stdc++fs linkage (not needed on macOS with modern clang)
    echo "  Applying no-stdc++fs.patch..."
    patch -p2 --batch < "${PATCHES_DIR}/no-stdc++fs.patch" || { echo "Error: Failed to apply no-stdc++fs.patch"; exit 1; }
    echo "  ✓ Applied no-stdc++fs.patch"

    # Patch 2: Fix reverse.hh.in - Remove malformed #elif directives for _OSSwapInt* functions
    echo "  Applying fix-reverse.hh.patch..."
    patch -p2 --batch < "${PATCHES_DIR}/fix-reverse.hh.patch" || { echo "Error: Failed to apply fix-reverse.hh.patch"; exit 1; }
    echo "  ✓ Applied fix-reverse.hh.patch"
fi

mkdir -p build && cd build
# Preserve environment CMAKE_PREFIX_PATH (from CI) and prepend our install prefix
COMBINED_PREFIX_PATH="$INSTALL_PREFIX${CMAKE_PREFIX_PATH:+:${CMAKE_PREFIX_PATH}}"
echo "CMAKE_PREFIX_PATH: $COMBINED_PREFIX_PATH"
cmake .. \
    "${CMAKE_COMMON_FLAGS[@]}" \
    -DCMAKE_INSTALL_PREFIX="$INSTALL_PREFIX" \
    -DCMAKE_PREFIX_PATH="$COMBINED_PREFIX_PATH" \
    -DBUILD_SHARED_LIBS=ON \
    -DBUILD_TESTING=OFF \
    -DENABLE_SWIG=OFF
cmake --build . --parallel "$NPROC"
cmake --install .

echo ""
echo "=========================================="
echo "4/4: Fetching and building ldas-tools-framecpp ${LDAS_TOOLS_FRAMECPP_VERSION}"
echo "=========================================="
cd "$BUILD_DIR"
fetch_and_extract "ldas-tools-framecpp" "$LDAS_TOOLS_FRAMECPP_VERSION" "$LDAS_TOOLS_FRAMECPP_URL"
cd "$BUILD_DIR/ldas-tools-framecpp-${LDAS_TOOLS_FRAMECPP_VERSION}"
mkdir -p build && cd build
# Preserve environment CMAKE_PREFIX_PATH (from CI) and prepend our install prefix
# CRITICAL: This ensures framecpp can find OpenSSL for MD5 support
COMBINED_PREFIX_PATH="$INSTALL_PREFIX${CMAKE_PREFIX_PATH:+:${CMAKE_PREFIX_PATH}}"
echo "CMAKE_PREFIX_PATH: $COMBINED_PREFIX_PATH"
cmake .. \
    "${CMAKE_COMMON_FLAGS[@]}" \
    -DCMAKE_INSTALL_PREFIX="$INSTALL_PREFIX" \
    -DCMAKE_PREFIX_PATH="$COMBINED_PREFIX_PATH" \
    -DCMAKE_INCLUDEDIR=include \
    -DBUILD_SHARED_LIBS=ON \
    -DBUILD_TESTING=OFF \
    -DENABLE_SWIG=OFF \
    -DENABLE_DOCUMENTATION_ONLY=OFF
cmake --build . --parallel "$NPROC"
cmake --install .

echo ""
echo "=========================================="
echo "Stripping debug symbols from libraries"
echo "=========================================="
# Strip debug symbols from libraries to reduce wheel size
if command -v strip &> /dev/null; then
    echo "Stripping libraries in $INSTALL_PREFIX..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS: use -x flag for stripping libraries
        find "$INSTALL_PREFIX" -name "*.a" -type f -exec strip -x {} \; 2>/dev/null || true
        find "$INSTALL_PREFIX" -name "*.dylib" -type f -exec strip -x {} \; 2>/dev/null || true
    else
        # Linux: use GNU strip flags
        find "$INSTALL_PREFIX" -name "*.a" -type f -exec strip --strip-debug {} \; 2>/dev/null || true
        find "$INSTALL_PREFIX" -name "*.so*" -type f -exec strip --strip-unneeded {} \; 2>/dev/null || true
    fi
    echo "Libraries stripped."
else
    echo "Warning: 'strip' command not found, skipping symbol stripping"
fi

# Keep shared libraries for dynamic linking + auditwheel/delocate bundling
# (Standard approach for binary wheels)

echo ""
echo "=========================================="
echo "LDAS Tools build complete!"
echo "=========================================="
echo "Installation prefix: $INSTALL_PREFIX"
echo ""
echo "Installed versions:"
echo "  - igwn-cmake-macros ${IGWN_CMAKE_VERSION} (from software.igwn.org)"
echo "  - ldas-tools-cmake ${LDAS_TOOLS_CMAKE_VERSION} (from software.igwn.org)"
echo "  - ldas-tools-al ${LDAS_TOOLS_AL_VERSION} (from software.ligo.org)"
echo "  - ldas-tools-framecpp ${LDAS_TOOLS_FRAMECPP_VERSION} (from software.igwn.org)"
echo ""
echo "CMake will find these libraries via:"
echo "  CMAKE_PREFIX_PATH=$INSTALL_PREFIX"
echo ""

# Show final library sizes
echo "Final library sizes:"
if [[ "$OSTYPE" == "darwin"* ]]; then
    find "$INSTALL_PREFIX" \( -name "*.dylib" -o -name "*.a" \) -type f | xargs du -h 2>/dev/null | sort -h || true
else
    find "$INSTALL_PREFIX" \( -name "*.so*" -o -name "*.a" \) -type f | xargs du -h 2>/dev/null | sort -h || true
fi
echo ""

# Verify installation
echo "Verifying installation..."
if command -v pkg-config &> /dev/null; then
    if pkg-config --exists framecpp; then
        FRAMECPP_VERSION=$(pkg-config --modversion framecpp)
        echo "✓ framecpp installed successfully at version ${FRAMECPP_VERSION}"
    else
        echo "⚠ Warning: pkg-config cannot find framecpp"
        echo "  This may be normal if PKG_CONFIG_PATH is not set yet"
    fi
else
    echo "⚠ Warning: pkg-config not available, cannot verify installation"
fi
echo ""
echo "Done!"
