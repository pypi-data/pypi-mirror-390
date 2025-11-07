# Installation

## From pip

```bash
pip install gwframe
```

The PyPI wheels are self-contained and include all necessary dependencies. No external libraries are required.

## From Conda

```bash
conda install -c conda-forge gwframe
```

## From Source

### Prerequisites

- Python 3.10 or newer
- NumPy >= 1.26
- CMake >= 3.15
- C++17-compatible compiler (GCC 7+, Clang 5+, MSVC 2017+)

### Quick Development Setup

Clone the repository and install in editable mode:

```bash
git clone https://git.ligo.org/patrick.godwin/gwframe.git
cd gwframe
pip install -e ".[dev]"
```

This installs gwframe with all development dependencies (pytest, mypy, ruff) and automatically builds the C++ extension.

### Using System frameCPP (Advanced)

If you have frameCPP already installed (e.g., via conda), you can link against it instead of building from source:

```bash
# Install frameCPP from conda-forge
conda install -c conda-forge ldas-tools-framecpp

# Build gwframe using system frameCPP
pip install . -C cmake.define.USE_SYSTEM_FRAMECPP=ON
```

This is faster for development as it uses shared linking and avoids rebuilding frameCPP.

### Building Wheels for Distribution

To create redistributable binary wheels:

**For Linux:**

```bash
# Build wheel
pip wheel . --no-deps -w dist/

# Bundle dependencies (makes it portable)
auditwheel repair dist/gwframe-*.whl -w dist/manylinux/
```

**For macOS:**

```bash
# Build wheel
pip wheel . --no-deps -w dist/

# Bundle dependencies
delocate-wheel -w dist/bundled/ dist/gwframe-*.whl
```

The bundled wheels can be distributed and installed on systems without frameCPP installed.

## Verifying Installation

To verify that gwframe is installed correctly:

```python
import gwframe
print(gwframe.__version__)
```

You can also run the test suite:

```bash
pytest src/gwframe/tests/
```

## Build Configuration

### Environment Variables

You can customize the build with these environment variables:

- **`CMAKE_BUILD_PARALLEL_LEVEL`**: Number of parallel build jobs (default: 1)
  ```bash
  CMAKE_BUILD_PARALLEL_LEVEL=4 pip install .
  ```

- **`CMAKE_PREFIX_PATH`**: Custom library search paths
  ```bash
  CMAKE_PREFIX_PATH=/opt/framecpp pip install .
  ```

## Dependencies

### Runtime Dependencies

- **NumPy** (>= 1.26)

### Build Dependencies

Only needed when building from source:

- **CMake** (>= 3.15): Build system
- **nanobind** (>= 2.0.0): C++/Python bindings (auto-installed)
- **frameCPP** (2.9.x): GW frame library (auto-built or system)

## Troubleshooting

### Import Errors

If you see `ImportError: cannot import name '_core'`:

1. Reinstall the package:
   ```bash
   pip install --force-reinstall --no-cache-dir gwframe
   ```

2. Verify Python version compatibility (3.10+):
   ```bash
   python --version
   ```

### Build Errors

Common solutions:

- **Compiler errors**: Ensure you have a C++17-compatible compiler
  - Linux: `gcc --version` (need GCC 7+)
  - macOS: `clang --version` (need Clang 5+)

- **CMake errors**: Update CMake
  ```bash
  pip install --upgrade cmake
  ```

- **Out of memory**: Reduce parallel jobs
  ```bash
  CMAKE_BUILD_PARALLEL_LEVEL=1 pip install .
  ```
