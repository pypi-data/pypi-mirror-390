#!/usr/bin/env python3
"""
Profile gwframe read operations.

Usage:
    # Profile with small file (500 iterations)
    py-spy record -o profile_read_small.svg -- python tools/profiling/profile_read.py --small

    # Profile with large file (100 iterations, good for Python overhead analysis)
    py-spy record -o profile_read_large.svg -- python tools/profiling/profile_read.py --large

    # Default: small file
    py-spy record -o profile_read.svg -- python tools/profiling/profile_read.py
"""

import argparse
import sys
from pathlib import Path

import gwframe

# Test files (relative to repo root)
TEST_FILE_SMALL = "src/gwframe/tests/data/L-L1_GWOSC_16KHZ_R1-1240215487-32.gwf"
CHANNEL_SMALL = "L1:GWOSC-16KHZ_R1_STRAIN"
TEST_FILE_LARGE = "H-H1_GWOSC_O4a_16KHZ_R1-1381289984-4096.gwf"
CHANNEL_LARGE = "H1:GWOSC-16KHZ_R1_STRAIN"


def main():
    parser = argparse.ArgumentParser(description="Profile gwframe read operations")
    parser.add_argument(
        "--large",
        action="store_true",
        help="Use large file (4096s, good for Python overhead analysis)",
    )
    parser.add_argument(
        "--small",
        action="store_true",
        help="Use small file (32s, more iterations)",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        help="Number of iterations (default: 500 for small, 100 for large)",
    )
    args = parser.parse_args()

    # Resolve paths relative to repo root
    repo_root = Path(__file__).parent.parent.parent

    # Determine file and iterations
    if args.large:
        test_file = repo_root / TEST_FILE_LARGE
        channel = CHANNEL_LARGE
        iterations = args.iterations or 100
        label = "large file (4096s)"
    else:
        test_file = repo_root / TEST_FILE_SMALL
        channel = CHANNEL_SMALL
        iterations = args.iterations or 500
        label = "small file (32s)"

    if not test_file.exists():
        print(f"Error: Test file '{test_file}' not found")
        sys.exit(1)

    print(f"Profiling gwframe read operations with {label}")
    print(f"Test file: {test_file}")
    print(f"Channel: {channel}")
    print(f"Iterations: {iterations}")
    print()
    print("Profiling in progress...")

    # Profile both TOC and frame reading
    for i in range(iterations):
        if i % 50 == 0:
            print(f"  Iteration {i}/{iterations}")

        # Profile TOC reading
        channels = gwframe.get_channels(str(test_file))

        # Profile frame reading
        data = gwframe.read(str(test_file), channel)

    print()
    print("Done! Analyze the output with py-spy flamegraph.")


if __name__ == "__main__":
    main()
