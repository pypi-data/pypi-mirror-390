#!/usr/bin/env python3
"""
Profile TOC/inspect operations (get_channels) for gwframe and SWIG.

This focuses specifically on the table of contents reading which showed
0.81x performance vs SWIG in benchmarks. High iteration count to identify
Python-layer overhead.

Usage:
    # Profile gwframe TOC operations
    py-spy record -o profile_inspect_gwframe.svg -- python tools/profiling/profile_inspect.py

    # Profile SWIG TOC operations for comparison
    py-spy record -o profile_inspect_swig.svg -- python tools/profiling/profile_inspect.py --swig
"""

import argparse
import sys
from pathlib import Path

# Test file (relative to repo root)
TEST_FILE = "src/gwframe/tests/data/L-L1_GWOSC_16KHZ_R1-1240215487-32.gwf"
N_ITERATIONS = 5000  # High iteration count since TOC is very fast (~0.4ms)


def profile_gwframe():
    """Profile gwframe get_channels operations."""
    import gwframe

    # Resolve path
    repo_root = Path(__file__).parent.parent.parent
    test_file = repo_root / TEST_FILE

    if not test_file.exists():
        print(f"Error: Test file '{test_file}' not found")
        sys.exit(1)

    print("Profiling gwframe get_channels operations...")
    print(f"Test file: {test_file}")
    print(f"Iterations: {N_ITERATIONS}")
    print(
        "Run with: py-spy record -o profile_inspect_gwframe.svg -- python tools/profiling/profile_inspect.py"
    )
    print()
    print("Profiling in progress...")

    for i in range(N_ITERATIONS):
        if i % 500 == 0:
            print(f"  Iteration {i}/{N_ITERATIONS}")

        # Profile TOC reading
        channels = gwframe.get_channels(str(test_file))

    print()
    print("Done! Analyze the output with py-spy flamegraph.")


def profile_swig():
    """Profile SWIG TOC operations."""
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

    print("Profiling SWIG GetTOC operations...")
    print(f"Test file: {test_file}")
    print(f"Iterations: {N_ITERATIONS}")
    print(
        "Run with: py-spy record -o profile_inspect_swig.svg -- python tools/profiling/profile_inspect.py --swig"
    )
    print()
    print("Profiling in progress...")

    for i in range(N_ITERATIONS):
        if i % 500 == 0:
            print(f"  Iteration {i}/{N_ITERATIONS}")

        # Profile TOC reading (matching what SWIG benchmark does)
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
