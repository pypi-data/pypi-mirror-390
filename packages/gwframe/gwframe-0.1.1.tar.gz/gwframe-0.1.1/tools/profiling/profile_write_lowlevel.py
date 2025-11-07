#!/usr/bin/env python3
"""
Profile low-level write operations for gwframe and SWIG (apples-to-apples).

This profiles the low-level C++ bindings directly, bypassing the Python layer,
for fair comparison with SWIG.

For profiling the actual high-level API users would call, use profile_write.py instead.

Usage:
    # Profile gwframe low-level operations
    py-spy record -o profile_write_lowlevel_gwframe.svg -- python tools/profiling/profile_write_lowlevel.py

    # Profile SWIG low-level operations for comparison
    py-spy record -o profile_write_lowlevel_swig.svg -- python tools/profiling/profile_write_lowlevel.py --swig

    # With native symbols (requires debug symbols)
    py-spy record --native -o profile_write_lowlevel_gwframe_native.svg -- python tools/profiling/profile_write_lowlevel.py

    # Higher sampling rate for more detail
    py-spy record --native --rate 500 -o profile_write_lowlevel_gwframe_hires.svg -- python tools/profiling/profile_write_lowlevel.py
"""

import argparse

import numpy as np

# Test data parameters
N_SAMPLES = 16384
SAMPLE_RATE = 16384
GPS_TIME = 1234567890
DURATION = 1.0
N_ITERATIONS = 10000  # Increased for better profiling resolution


def profile_gwframe():
    """Profile gwframe write operations."""
    import gwframe._core as core

    data = np.sin(np.linspace(0, 2 * np.pi, N_SAMPLES))

    print("Profiling gwframe low-level write operations...")
    print(f"Iterations: {N_ITERATIONS}")
    print(
        "Run with: py-spy record --native -o profile_write_lowlevel_gwframe.svg -- python tools/profiling/profile_write_lowlevel.py"
    )
    print()

    for i in range(N_ITERATIONS):
        if i % 50 == 0:
            print(f"  Iteration {i}/{N_ITERATIONS}")

        # Low-level API (matching SWIG for fair comparison)
        frame = core.FrameH()
        frame.set_name("TEST")
        frame.set_gps_time(core.GPSTime(GPS_TIME, 0))
        frame.set_dt(DURATION)
        frame.set_run(-1)

        dim = core.Dimension(N_SAMPLES, 1.0 / SAMPLE_RATE, "s", 0.0)
        vect = core.FrVect("TEST:CHANNEL", core.FrVect.FR_VECT_8R, 1, dim, "")
        vect.get_data_array()[:] = data  # Match SWIG pattern

        frdata = core.FrProcData(
            "TEST:CHANNEL", "", 1, 0, 0.0, DURATION, 0.0, 0.0, 0.0, 0.0
        )
        frdata.append_data(vect)
        frame.append_fr_proc_data(frdata)
        frame.write(core.OFrameFStream(f"/tmp/test_profile_gwframe_{i}.gwf"))

    print()
    print("Done! Analyze the output with py-spy flamegraph.")


def profile_swig():
    """Profile SWIG write operations."""
    try:
        from LDAStools import frameCPP as frcpp
    except ImportError:
        print("Error: LDAStools.frameCPP (SWIG) not available")
        print("Install with: conda install -c conda-forge ldas-tools-framecpp")
        return

    data = np.sin(np.linspace(0, 2 * np.pi, N_SAMPLES))

    print("Profiling SWIG low-level write operations...")
    print(f"Iterations: {N_ITERATIONS}")
    print(
        "Run with: py-spy record --native -o profile_write_lowlevel_swig.svg -- python tools/profiling/profile_write_lowlevel.py --swig"
    )
    print()

    for i in range(N_ITERATIONS):
        if i % 50 == 0:
            print(f"  Iteration {i}/{N_ITERATIONS}")

        # SWIG API
        frame = frcpp.FrameH()
        frame.SetName("TEST")
        frame.SetGTime(frcpp.GPSTime(GPS_TIME, 0))
        frame.SetDt(DURATION)
        frame.SetRun(-1)

        dim = frcpp.Dimension(N_SAMPLES, 1.0 / SAMPLE_RATE, "s", 0.0)
        vect = frcpp.FrVect("TEST:CHANNEL", frcpp.FrVect.FR_VECT_8R, 1, dim, "")
        vect.GetDataArray()[:] = data

        frdata = frcpp.FrProcData(
            "TEST:CHANNEL",
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
        frame.Write(frcpp.OFrameFStream("/tmp/test_profile_swig.gwf"))

    print()
    print("Done! Analyze the output with py-spy flamegraph.")


def main():
    parser = argparse.ArgumentParser(description="Profile write operations")
    parser.add_argument(
        "--swig",
        action="store_true",
        help="Profile SWIG implementation instead of gwframe",
    )
    args = parser.parse_args()

    if args.swig:
        profile_swig()
    else:
        profile_gwframe()


if __name__ == "__main__":
    main()
