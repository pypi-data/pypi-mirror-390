#!/usr/bin/env python3
"""
Profile high-level write API for gwframe.

This profiles the actual API users would use (gwframe.write() function),
which includes the Python layer overhead from the Frame class.

Usage:
    py-spy record -o profile_write_gwframe.svg -- python tools/profiling/profile_write.py
"""

import numpy as np

# Test data parameters
N_SAMPLES = 16384
SAMPLE_RATE = 16384
GPS_TIME = 1234567890
N_ITERATIONS = 5000


def profile_gwframe():
    """Profile gwframe.write() high-level API."""
    import gwframe

    data = np.sin(np.linspace(0, 2 * np.pi, N_SAMPLES))

    print("Profiling gwframe.write() high-level API...")
    print(f"Iterations: {N_ITERATIONS}")
    print(
        "Run with: py-spy record -o profile_write_gwframe.svg -- python tools/profiling/profile_write.py"
    )
    print()

    for i in range(N_ITERATIONS):
        if i % 500 == 0:
            print(f"  Iteration {i}/{N_ITERATIONS}")

        # High-level write() function (what users actually call)
        gwframe.write(
            f"/tmp/test_profile_highlevel_{i}.gwf",
            data,
            t0=GPS_TIME,
            sample_rate=SAMPLE_RATE,
            name="TEST:CHANNEL",
            unit="strain",
        )

    print()
    print("Done! Analyze the output with py-spy flamegraph.")
    print("Compare with profile_write_lowlevel.py to see Python layer overhead.")


if __name__ == "__main__":
    profile_gwframe()
