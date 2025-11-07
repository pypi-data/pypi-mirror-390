#!/usr/bin/env python3
"""
Profile low-level read operations for gwframe and SWIG (apples-to-apples).

This profiles the low-level C++ bindings directly, bypassing the Python layer,
for fair comparison with SWIG.

For profiling the actual high-level API users would call, use profile_read.py instead.

Usage:
    # Profile gwframe low-level operations (small file)
    py-spy record -o profile_read_lowlevel_gwframe.svg -- python tools/profiling/profile_read_lowlevel.py

    # Profile SWIG low-level operations for comparison
    py-spy record -o profile_read_lowlevel_swig.svg -- python tools/profiling/profile_read_lowlevel.py --swig

    # Use large file for more time in C++
    py-spy record -o profile_read_lowlevel_gwframe_large.svg -- python tools/profiling/profile_read_lowlevel.py --large

    # With native symbols (requires debug symbols)
    py-spy record --native -o profile_read_lowlevel_gwframe_native.svg -- python tools/profiling/profile_read_lowlevel.py

    # Higher sampling rate for more detail
    py-spy record --native --rate 500 -o profile_read_lowlevel_gwframe_hires.svg -- python tools/profiling/profile_read_lowlevel.py
"""

import argparse
import sys
from pathlib import Path

import numpy as np

# Test files (relative to repo root)
TEST_FILE_SMALL = "src/gwframe/tests/data/L-L1_GWOSC_16KHZ_R1-1240215487-32.gwf"
CHANNEL_SMALL = "L1:GWOSC-16KHZ_R1_STRAIN"
TEST_FILE_LARGE = "H-H1_GWOSC_O4a_16KHZ_R1-1381289984-4096.gwf"
CHANNEL_LARGE = "H1:GWOSC-16KHZ_R1_STRAIN"
N_ITERATIONS_SMALL = 1000  # Reduced for reasonable profiling time
N_ITERATIONS_LARGE = 20  # Large file is slow, use fewer iterations


def profile_gwframe(test_file, channel, iterations):
    """Profile gwframe read operations using low-level C++ bindings."""
    import gwframe._core as core

    print("Profiling gwframe low-level read operations...")
    print(f"Test file: {test_file}")
    print(f"Channel: {channel}")
    print(f"Iterations: {iterations}")
    print(
        "Run with: py-spy record --native -o profile_read_lowlevel_gwframe.svg -- python tools/profiling/profile_read_lowlevel.py"
    )
    print()

    for i in range(iterations):
        if i % 50 == 0:
            print(f"  Iteration {i}/{iterations}")

        # Low-level API (matching SWIG for fair comparison)
        ifo = core.IFrameFStream(str(test_file))
        frdata = ifo.read_fr_proc_data(0, channel)
        vect = frdata.get_data_vector(0)
        data = vect.get_data_array()

    print()
    print("Done! Analyze the output with py-spy flamegraph.")


def profile_swig(test_file, channel, iterations):
    """Profile SWIG read operations using low-level C++ bindings."""
    try:
        from LDAStools import frameCPP as frcpp
    except ImportError:
        print("Error: LDAStools.frameCPP (SWIG) not available")
        print("Install with: conda install -c conda-forge ldas-tools-framecpp")
        return

    print("Profiling SWIG low-level read operations...")
    print(f"Test file: {test_file}")
    print(f"Channel: {channel}")
    print(f"Iterations: {iterations}")
    print(
        "Run with: py-spy record --native -o profile_read_lowlevel_swig.svg -- python tools/profiling/profile_read_lowlevel.py --swig"
    )
    print()

    for i in range(iterations):
        if i % 50 == 0:
            print(f"  Iteration {i}/{iterations}")

        # SWIG API
        ifo = frcpp.IFrameFStream(str(test_file))
        frdata = ifo.ReadFrProcData(0, channel)
        vect = frdata.RefData()[0]
        data = np.require(vect.GetDataArray(), requirements=["O"])

    print()
    print("Done! Analyze the output with py-spy flamegraph.")


def main():
    parser = argparse.ArgumentParser(description="Profile read operations")
    parser.add_argument(
        "--swig",
        action="store_true",
        help="Profile SWIG implementation instead of gwframe",
    )
    parser.add_argument(
        "--large",
        action="store_true",
        help="Use large file (4096s, more time in C++)",
    )
    args = parser.parse_args()

    # Resolve paths relative to repo root
    repo_root = Path(__file__).parent.parent.parent

    # Determine file and iterations
    if args.large:
        test_file = repo_root / TEST_FILE_LARGE
        channel = CHANNEL_LARGE
        iterations = N_ITERATIONS_LARGE
    else:
        test_file = repo_root / TEST_FILE_SMALL
        channel = CHANNEL_SMALL
        iterations = N_ITERATIONS_SMALL

    if not test_file.exists():
        print(f"Error: Test file '{test_file}' not found")
        sys.exit(1)

    if args.swig:
        profile_swig(test_file, channel, iterations)
    else:
        profile_gwframe(test_file, channel, iterations)


if __name__ == "__main__":
    main()
