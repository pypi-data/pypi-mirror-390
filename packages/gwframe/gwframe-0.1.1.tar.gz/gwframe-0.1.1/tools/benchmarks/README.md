# Benchmarks

Performance benchmarks comparing gwframe with LDAStools.frameCPP (SWIG bindings).

## Files

### benchmark_performance.py
Comprehensive performance benchmark covering:
- Reading table of contents (TOC)
- Reading full frame data (small and large files)
- Writing frame data (high-level API)

Run from repository root:
```bash
python tools/benchmarks/benchmark_performance.py
```

### benchmark_lowlevel.py
Apples-to-apples comparison of low-level APIs (gwframe._core vs SWIG).
Tests the raw binding performance without Python convenience wrappers.

Run from repository root:
```bash
python tools/benchmarks/benchmark_lowlevel.py
```

### benchmark_compression.py
Compression algorithm comparison:
- RAW (no compression)
- GZIP (various levels)
- ZERO_SUPPRESS_OTHERWISE_GZIP (default)

Measures write time, file size, and throughput for each compression scheme.

Run from repository root:
```bash
python tools/benchmarks/benchmark_compression.py
```

## Requirements

All benchmarks require:
- gwframe installed
- LDAStools.frameCPP (SWIG) installed for comparison
- Test files in `tests/` directory

## Expected Results

Performance should be on par between gwframe and SWIG bindings, with gwframe
providing a more Pythonic interface.
