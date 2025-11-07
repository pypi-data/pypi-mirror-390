#!/usr/bin/env python3
"""
Profile low-level TOC/inspect operations for gwframe and SWIG (apples-to-apples).

This profiles the low-level C++ bindings directly, bypassing the Python layer,
for fair comparison with SWIG.

For profiling the actual high-level API users would call, use profile_inspect.py instead.

Usage:
    # Profile gwframe low-level operations
    py-spy record -o profile_inspect_lowlevel_gwframe.svg -- python tools/profiling/profile_inspect_lowlevel.py

    # Profile SWIG low-level operations for comparison
    py-spy record -o profile_inspect_lowlevel_swig.svg -- python tools/profiling/profile_inspect_lowlevel.py --swig

    # With native symbols (requires debug symbols)
    py-spy record --native -o profile_inspect_lowlevel_gwframe_native.svg -- python tools/profiling/profile_inspect_lowlevel.py

    # Higher sampling rate for more detail
    py-spy record --native --rate 500 -o profile_inspect_lowlevel_gwframe_hires.svg -- python tools/profiling/profile_inspect_lowlevel.py
"""

import argparse
import sys
from pathlib import Path

# Test file (relative to repo root)
TEST_FILE = "src/gwframe/tests/data/L-L1_GWOSC_16KHZ_R1-1240215487-32.gwf"
N_ITERATIONS = 10000  # High iteration count since TOC is very fast (~0.4ms)


def profile_gwframe():
    """Profile gwframe get_toc operations using low-level C++ bindings."""
    import gwframe._core as core

    # Resolve path
    repo_root = Path(__file__).parent.parent.parent
    test_file = repo_root / TEST_FILE

    if not test_file.exists():
        print(f"Error: Test file '{test_file}' not found")
        sys.exit(1)

    print("Profiling gwframe low-level get_toc operations...")
    print(f"Test file: {test_file}")
    print(f"Iterations: {N_ITERATIONS}")
    print(
        "Run with: py-spy record --native -o profile_inspect_lowlevel_gwframe.svg -- python tools/profiling/profile_inspect_lowlevel.py"
    )
    print()
    print("Profiling in progress...")

    for i in range(N_ITERATIONS):
        if i % 500 == 0:
            print(f"  Iteration {i}/{N_ITERATIONS}")

        # Low-level API (matching SWIG for fair comparison)
        ifo = core.IFrameFStream(str(test_file))
        toc = ifo.get_toc()
        adc = toc.get_adc()
        proc = toc.get_proc()
        sim = toc.get_sim()

    print()
    print("Done! Analyze the output with py-spy flamegraph.")


def profile_swig():
    """Profile SWIG GetTOC operations using low-level C++ bindings."""
    try:
        from LDAStools import frameCPP as frcpp
    except ImportError:
        print("Error: LDAStools.frameCPP (SWIG) not available")
        print("Install with: conda install -c conda-forge ldas-tools-framecpp")
        return

    # Resolve path
    repo_root = Path(__file__).parent.parent.parent
    test_file = repo_root / TEST_FILE

    if not test_file.exists():
        print(f"Error: Test file '{test_file}' not found")
        sys.exit(1)

    print("Profiling SWIG low-level GetTOC operations...")
    print(f"Test file: {test_file}")
    print(f"Iterations: {N_ITERATIONS}")
    print(
        "Run with: py-spy record --native -o profile_inspect_lowlevel_swig.svg -- python tools/profiling/profile_inspect_lowlevel.py --swig"
    )
    print()
    print("Profiling in progress...")

    for i in range(N_ITERATIONS):
        if i % 500 == 0:
            print(f"  Iteration {i}/{N_ITERATIONS}")

        # SWIG API
        ifo = frcpp.IFrameFStream(str(test_file))
        toc = ifo.GetTOC()
        adc = list(toc.GetADC())
        proc = list(toc.GetProc())
        sim = list(toc.GetSim())

    print()
    print("Done! Analyze the output with py-spy flamegraph.")


def main():
    parser = argparse.ArgumentParser(description="Profile TOC/inspect operations")
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
