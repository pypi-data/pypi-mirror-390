#!/usr/bin/env python3
"""
Benchmark low-level nanobind API directly (apples-to-apples with SWIG)

This benchmarks the raw C++ bindings layer, comparing nanobind vs SWIG.
Uses the same L1 data as benchmark_performance.py for consistency.
"""

import time

import gwframe._core as core
import numpy as np

import gwframe

# Read realistic data (32s file - same as high-level benchmark for fair comparison)
from pathlib import Path
repo_root = Path(__file__).parent.parent.parent
TEST_FILE = str(repo_root / "src/gwframe/tests/data/L-L1_GWOSC_16KHZ_R1-1240215487-32.gwf")
CHANNEL = "L1:GWOSC-16KHZ_R1_STRAIN"
N_ITERATIONS = 30  # Increased for more stable measurements

print("=" * 80)
print("Low-Level API Comparison (Apples-to-Apples)")
print("=" * 80)

# Read full 32s file for benchmarking (same data as high-level benchmark)
result = gwframe.read(TEST_FILE, CHANNEL)
data = result.array
t0 = result.t0
dt = result.dt
GPS_TIME = int(t0)
DURATION = len(data) * dt

print(f"\nData: {len(data)} samples, {data.nbytes / 1024 / 1024:.2f} MB\n")

# Benchmark nanobind low-level API (exactly like SWIG)
print("=" * 80)
print("Nanobind low-level API (matching SWIG benchmark)")
print("=" * 80)

times_nb = []
for i in range(N_ITERATIONS):
    start = time.perf_counter()

    # Build frame using low-level API (matching SWIG for fair comparison)
    frame = core.FrameH()
    frame.set_name("L1")
    frame.set_gps_time(core.GPSTime(GPS_TIME, 0))  # Match SWIG pattern
    frame.set_dt(DURATION)
    frame.set_run(-1)

    dim = core.Dimension(len(data), dt, "s", 0.0)
    vect = core.FrVect("L1:TEST-STRAIN", core.FrVect.FR_VECT_8R, 1, dim, "")
    vect.get_data_array()[:] = data  # Match SWIG pattern

    frdata = core.FrProcData(
        "L1:TEST-STRAIN", "", 1, 0, 0.0, DURATION, 0.0, 0.0, 0.0, 0.0
    )
    frdata.append_data(vect)
    frame.append_fr_proc_data(frdata)
    frame.write(core.OFrameFStream(f"/tmp/test_nb_lowlevel_{i}.gwf"))

    elapsed = time.perf_counter() - start
    times_nb.append(elapsed)
    if i == 0:
        print(f"  Iteration {i + 1}: {elapsed * 1000:.2f} ms")

times_nb = times_nb[1:]
avg_nb = np.mean(times_nb) * 1000
std_nb = np.std(times_nb) * 1000
print("\nResults (after warmup):")
print(f"  Mean: {avg_nb:.2f} ms")
print(f"  Std:  {std_nb:.2f} ms")
print(f"  Throughput: {data.nbytes / np.mean(times_nb) / 1024 / 1024:.1f} MB/s")

# Benchmark SWIG
print(f"\n{'=' * 80}")
print("SWIG API")
print("=" * 80)

from LDAStools import frameCPP as frcpp

times_swig = []
for i in range(N_ITERATIONS):
    start = time.perf_counter()

    frame = frcpp.FrameH()
    frame.SetName("L1")
    frame.SetGTime(frcpp.GPSTime(GPS_TIME, 0))
    frame.SetDt(DURATION)
    frame.SetRun(-1)

    dim = frcpp.Dimension(len(data), dt, "s", 0.0)
    vect = frcpp.FrVect("L1:TEST-STRAIN", frcpp.FrVect.FR_VECT_8R, 1, dim, "")
    vect.GetDataArray()[:] = data

    frdata = frcpp.FrProcData(
        "L1:TEST-STRAIN",
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
    frame.Write(frcpp.OFrameFStream(f"/tmp/test_swig_lowlevel_{i}.gwf"))

    elapsed = time.perf_counter() - start
    times_swig.append(elapsed)
    if i == 0:
        print(f"  Iteration {i + 1}: {elapsed * 1000:.2f} ms")

times_swig = times_swig[1:]
avg_swig = np.mean(times_swig) * 1000
std_swig = np.std(times_swig) * 1000
print("\nResults (after warmup):")
print(f"  Mean: {avg_swig:.2f} ms")
print(f"  Std:  {std_swig:.2f} ms")
print(f"  Throughput: {data.nbytes / np.mean(times_swig) / 1024 / 1024:.1f} MB/s")

# Compare
print(f"\n{'=' * 80}")
print("Comparison (Apples-to-Apples)")
print("=" * 80)
print(f"Nanobind low-level: {avg_nb:.2f} ms (±{std_nb:.2f})")
print(f"SWIG:               {avg_swig:.2f} ms (±{std_swig:.2f})")
ratio = avg_nb / avg_swig
print(f"\nSWIG is {ratio:.2f}x faster")
print(f"Absolute difference: {abs(avg_nb - avg_swig):.2f} ms")
print("=" * 80)
