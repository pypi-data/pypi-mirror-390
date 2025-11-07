# Build Patches for LDAS Tools

These patches fix compatibility and configuration issues in LDAS Tools builds. Some are from conda-forge feedstocks, others are custom fixes.

## ldas-tools-al Patches (from conda-forge)

Source: https://github.com/conda-forge/ldas-tools-al-feedstock/tree/main/recipe

### 1. no-stdc++fs.patch

**Purpose**: Removes `stdc++fs` library linkage which is not needed on modern macOS with clang.

**Reason**: Modern clang on macOS has C++17 filesystem support integrated into `libc++`, so the separate `stdc++fs` library is not needed and causes linker errors.

**Files Modified**:
- `ldastoolsal/src/CMakeLists.txt` - Removes `stdc++fs` from link libraries
- `ldastoolsal/src/ldastoolsal.pc.in` - Removes `stdc++fs` from pkg-config Libs

**Upstream**: https://github.com/conda-forge/ldas-tools-al-feedstock/blob/main/recipe/no-stdc%2B%2Bfs.patch

### 2. fix-reverse.hh.patch

**Purpose**: Fixes malformed preprocessor directives in `reverse.hh.in` that cause compilation errors.

**Reason**: The template contains `#elif @HAVE__OSSWAPINT16@` which, when CMake variables are not set, expands to `#elif  // HAVE__OSSWAPINT16` (invalid C preprocessor syntax). This causes "expected value in expression" errors during compilation.

**Files Modified**:
- `ldastoolsal/src/reverse.hh.in` - Removes three `#elif` blocks for underscore-prefixed swap functions (`_OSSwapInt16`, `_OSSwapInt32`, `_OSSwapInt64`)

**Impact**: The non-underscore variants (`OSSwapInt16`, `OSSwapInt32`, `OSSwapInt64`) are still available and are used on modern macOS.

**Upstream**: https://github.com/conda-forge/ldas-tools-al-feedstock/blob/main/recipe/fix-reverse.hh.patch

## Application

Patches are applied when building on macOS (`$OSTYPE == "darwin"*`).
