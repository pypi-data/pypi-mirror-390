#!/usr/bin/env python3
"""
Benchmark different compression algorithms and their performance impact.

Tests:
1. RAW (no compression)
2. GZIP (standard compression)
3. ZERO_SUPPRESS_OTHERWISE_GZIP (hybrid, SWIG default)
"""

import os
import sys
import time
from pathlib import Path

import gwframe._core as core
import numpy as np

import gwframe

# Test with 32-second slice from 4096s file at 16kHz (~512k samples, 4MB)
TEST_FILE = "H-H1_GWOSC_O4a_16KHZ_R1-1381289984-4096.gwf"
CHANNEL = "H1:GWOSC-16KHZ_R1_STRAIN"
N_ITERATIONS = 30  # Increased for more stable measurements


def benchmark_compression(data, t0, dt, compression, compression_level, name):
    """Benchmark a specific compression scheme."""
    GPS_TIME = int(t0)
    DURATION = len(data) * dt

    times = []
    file_sizes = []

    for i in range(N_ITERATIONS):
        filename = f"/tmp/test_{name}_{i}.gwf"

        # Build frame using low-level API (matching SWIG for fair comparison)
        frame = core.FrameH()
        frame.set_name("L1")
        frame.set_gps_time(core.GPSTime(GPS_TIME, 0))  # Match SWIG pattern
        frame.set_dt(DURATION)
        frame.set_run(-1)

        dim = core.Dimension(len(data), dt, "s", 0.0)
        vect = core.FrVect("L1:TEST", core.FrVect.FR_VECT_8R, 1, dim, "")
        vect.get_data_array()[:] = data  # Match SWIG pattern

        frdata = core.FrProcData("L1:TEST", "", 1, 0, 0.0, DURATION, 0.0, 0.0, 0.0, 0.0)
        frdata.append_data(vect)
        frame.append_fr_proc_data(frdata)

        # Time the write
        start = time.perf_counter()
        frame.write(
            core.OFrameFStream(filename),
            compression=compression,
            compression_level=compression_level,
        )
        elapsed = time.perf_counter() - start
        times.append(elapsed)

        # Record file size
        file_sizes.append(os.path.getsize(filename))

    # Remove warmup iteration
    times = times[1:]
    file_sizes = file_sizes[1:]

    avg_time = np.mean(times) * 1000
    std_time = np.std(times) * 1000
    avg_size = np.mean(file_sizes) / 1024 / 1024
    throughput = data.nbytes / np.mean(times) / 1024 / 1024

    return {
        "avg_time": avg_time,
        "std_time": std_time,
        "avg_size": avg_size,
        "throughput": throughput,
    }


def benchmark_swig_compression(data, t0, dt):
    """Benchmark SWIG with default ZERO_SUPPRESS_OTHERWISE_GZIP compression."""
    try:
        from LDAStools import frameCPP as frcpp

        GPS_TIME = int(t0)
        DURATION = len(data) * dt

        times = []
        file_sizes = []

        for i in range(N_ITERATIONS):
            filename = f"/tmp/test_swig_default_{i}.gwf"

            frame = frcpp.FrameH()
            frame.SetName("L1")
            frame.SetGTime(frcpp.GPSTime(GPS_TIME, 0))
            frame.SetDt(DURATION)
            frame.SetRun(-1)

            dim = frcpp.Dimension(len(data), dt, "s", 0.0)
            vect = frcpp.FrVect("L1:TEST", frcpp.FrVect.FR_VECT_8R, 1, dim, "")
            vect.GetDataArray()[:] = data

            frdata = frcpp.FrProcData(
                "L1:TEST",
                "",
                frcpp.FrProcData.TIME_SERIES,
                frcpp.FrProcData.UNKNOWN_SUB_TYPE,
                0.0,
                DURATION,
                0.0,
                0.0,
                0.0,
                0.0,
            )
            frdata.AppendData(vect)
            frame.AppendFrProcData(frdata)

            start = time.perf_counter()
            frame.Write(frcpp.OFrameFStream(filename))
            elapsed = time.perf_counter() - start
            times.append(elapsed)

            file_sizes.append(os.path.getsize(filename))

        times = times[1:]
        file_sizes = file_sizes[1:]

        avg_time = np.mean(times) * 1000
        std_time = np.std(times) * 1000
        avg_size = np.mean(file_sizes) / 1024 / 1024
        throughput = data.nbytes / np.mean(times) / 1024 / 1024

        return {
            "avg_time": avg_time,
            "std_time": std_time,
            "avg_size": avg_size,
            "throughput": throughput,
        }

    except ImportError:
        return None


def main():
    # Resolve path relative to repo root
    repo_root = Path(__file__).parent.parent.parent
    test_file = repo_root / TEST_FILE

    if not test_file.exists():
        print(f"Error: Test file '{test_file}' not found")
        sys.exit(1)

    print("=" * 80)
    print("Compression Algorithm Benchmark")
    print("=" * 80)

    # Read test data (32s slice)
    print(f"\nReading test file: {test_file} (32s slice)")
    result = gwframe.read(str(test_file), CHANNEL, start=1381289984.0, end=1381290016.0)
    data = result.array
    t0 = result.t0
    dt = result.dt

    print(f"  Data shape: {data.shape}")
    print(f"  Data size: {data.nbytes / 1024 / 1024:.2f} MB")
    print(f"  Sample rate: {1 / dt:.0f} Hz")
    print(f"  Duration: {len(data) * dt:.1f} seconds")

    # Benchmark different compression schemes
    print(f"\n{'=' * 80}")
    print("Testing gwframe compression schemes")
    print("=" * 80)

    compressions = [
        (0, 0, "RAW (no compression)"),
        (257, 6, "GZIP (level 6)"),
        (257, 9, "GZIP (level 9, best compression)"),
        (6, 6, "ZERO_SUPPRESS_OTHERWISE_GZIP (default)"),
    ]

    results = {}
    for comp, level, name in compressions:
        print(f"\nBenchmarking: {name}")
        result = benchmark_compression(data, t0, dt, comp, level, name.split()[0])
        results[name] = result
        print(f"  Time:       {result['avg_time']:.2f} ms (±{result['std_time']:.2f})")
        print(f"  File size:  {result['avg_size']:.2f} MB")
        print(f"  Throughput: {result['throughput']:.1f} MB/s")

    # Benchmark SWIG for comparison
    print(f"\n{'=' * 80}")
    print("Testing SWIG default compression (ZERO_SUPPRESS_OTHERWISE_GZIP)")
    print("=" * 80)

    swig_result = benchmark_swig_compression(data, t0, dt)
    if swig_result:
        results["SWIG (default)"] = swig_result
        print(
            f"  Time:       {swig_result['avg_time']:.2f} ms (±{swig_result['std_time']:.2f})"
        )
        print(f"  File size:  {swig_result['avg_size']:.2f} MB")
        print(f"  Throughput: {swig_result['throughput']:.1f} MB/s")
    else:
        print("  SWIG not available for comparison")

    # Summary table
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print("=" * 80)
    print(
        f"{'Compression Scheme':<40s} {'Time (ms)':>12s} {'Size (MB)':>12s} {'Throughput':>12s}"
    )
    print("-" * 80)

    for name, result in results.items():
        print(
            f"{name:<40s} {result['avg_time']:>10.2f}   {result['avg_size']:>10.2f}   {result['throughput']:>10.1f} MB/s"
        )

    # Size comparison
    if "RAW (no compression)" in results:
        raw_size = results["RAW (no compression)"]["avg_size"]
        print(f"\n{'Compression Ratios (vs RAW):':<40s}")
        print("-" * 80)
        for name, result in results.items():
            if name != "RAW (no compression)":
                ratio = raw_size / result["avg_size"]
                print(f"{name:<40s} {ratio:>10.2f}x")

    # Speed comparison
    if "RAW (no compression)" in results:
        raw_time = results["RAW (no compression)"]["avg_time"]
        print(f"\n{'Speed Overhead (vs RAW):':<40s}")
        print("-" * 80)
        for name, result in results.items():
            if name != "RAW (no compression)":
                overhead = (result["avg_time"] / raw_time - 1) * 100
                print(f"{name:<40s} {overhead:>10.1f}%")

    print("=" * 80)


if __name__ == "__main__":
    main()
