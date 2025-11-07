# Profiling Tools

Profiling scripts for analyzing gwframe performance characteristics using tools like `py-spy`.

## Files

### profile_read.py
Profile read operations (TOC + frame data) with configurable file size.

Usage:
```bash
# Profile with small file (500 iterations, fast)
py-spy record -o profile_read_small.svg -- python tools/profiling/profile_read.py --small

# Profile with large file (100 iterations, good for Python overhead analysis)
py-spy record -o profile_read_large.svg -- python tools/profiling/profile_read.py --large

# Custom iteration count
py-spy record -o profile_read.svg -- python tools/profiling/profile_read.py --iterations 1000
```

### profile_write.py
Profile write operations for gwframe or SWIG (for comparison).

Usage:
```bash
# Profile gwframe write operations
py-spy record -o profile_write_gwframe.svg -- python tools/profiling/profile_write.py

# Profile SWIG write operations for comparison
py-spy record -o profile_write_swig.svg -- python tools/profiling/profile_write.py --swig
```

## Requirements

- `py-spy` for profiling: `pip install py-spy`
- gwframe installed
- LDAStools.frameCPP (SWIG) for SWIG comparison profiles
- Test files in `tests/` directory

## Analyzing Results

View flamegraphs with any SVG viewer or browser:
```bash
firefox profile_read.svg
```

Or use `snakeviz` for interactive analysis:
```bash
pip install snakeviz
snakeviz profile.json
```
