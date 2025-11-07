#!/usr/bin/env python3
"""
Comprehensive performance benchmark: gwframe vs LDAStools.frameCPP (SWIG)

This script benchmarks:
1. Reading table of contents (TOC)
2. Reading full frame data
3. Writing frame data (high-level API)
"""

import sys
import time
from pathlib import Path

import numpy as np

# Test files (relative to repo root)
TEST_FILE_SMALL = "src/gwframe/tests/data/L-L1_GWOSC_16KHZ_R1-1240215487-32.gwf"
TEST_FILE_LARGE = "H-H1_GWOSC_O4a_16KHZ_R1-1381289984-4096.gwf"
CHANNEL_SMALL = "L1:GWOSC-16KHZ_R1_STRAIN"
CHANNEL_LARGE = "H1:GWOSC-16KHZ_R1_STRAIN"

N_ITERATIONS_TOC = 100  # TOC is fast (~0.7ms), can do many iterations
N_ITERATIONS_READ_SMALL = 100  # Small file reads are fast (~20ms)
N_ITERATIONS_READ_LARGE = 20  # Large file reads are slow (~2.5s each)
N_ITERATIONS_WRITE = 50  # Writes are fast (~12ms), can do more


def benchmark_function(func, name, n=N_ITERATIONS_TOC):
    """Benchmark a function with multiple iterations."""
    times = []

    # Warmup
    for _ in range(5):
        func()

    # Actual benchmark
    for _ in range(n):
        start = time.perf_counter()
        result = func()
        end = time.perf_counter()
        times.append(end - start)

    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    print(
        f"  {name:40s} {avg_time * 1000:8.3f} ms  (min: {min_time * 1000:.3f} ms, max: {max_time * 1000:.3f} ms)"
    )

    return avg_time, result


def benchmark_read_file(
    test_file, channel, n_iterations_toc, n_iterations_read, file_label=""
):
    """Benchmark read operations on a specific file."""
    print("\n" + "=" * 80)
    print(f"Read Benchmark: {file_label}")
    print("=" * 80)
    print(f"Test file: {test_file}")
    print(f"Channel: {channel}")
    print(f"TOC Iterations: {n_iterations_toc}, Read Iterations: {n_iterations_read}")
    print()

    # ========================================================================
    # Benchmark 1: Reading Table of Contents
    # ========================================================================
    print("=" * 80)
    print("Benchmark 1: Reading Table of Contents")
    print("=" * 80)

    # gwframe
    try:
        import gwframe

        def gwframe_toc():
            return gwframe.get_channels(test_file)

        print("\ngwframe (nanobind):")
        gwframe_toc_time, gwframe_toc_result = benchmark_function(
            gwframe_toc, "get_channels()", n_iterations_toc
        )
        print(f"  Channels found: {len(gwframe_toc_result)} total")

    except ImportError as e:
        print(f"\ngwframe not available: {e}")
        gwframe_toc_time = None

    # SWIG bindings
    try:
        from LDAStools import frameCPP as swig_framecpp

        def swig_toc():
            ifo = swig_framecpp.IFrameFStream(test_file)
            toc = ifo.GetTOC()
            # Get channel lists (these return Python lists directly)
            adc = list(toc.GetADC())
            proc = list(toc.GetProc())
            sim = list(toc.GetSim())
            return (adc, proc, sim)

        print("\nLDAStools.frameCPP (SWIG):")
        swig_toc_time, swig_toc_result = benchmark_function(
            swig_toc, "IFrameFStream().GetTOC()", n_iterations_toc
        )
        print(f"  Channels found: {sum(len(v) for v in swig_toc_result)} total")

    except ImportError as e:
        print(f"\nLDAStools.frameCPP (SWIG) not available: {e}")
        swig_toc_time = None

    # Compare
    if gwframe_toc_time and swig_toc_time:
        speedup = swig_toc_time / gwframe_toc_time
        print(f"\n{'=' * 80}")
        print(
            f"TOC Reading Speedup: {speedup:.2f}x {'FASTER' if speedup > 1 else 'SLOWER'}"
        )
        print(f"{'=' * 80}")

    # ========================================================================
    # Benchmark 2: Reading Full Frame Data
    # ========================================================================
    print("\n\n" + "=" * 80)
    print("Benchmark 2: Reading Full Frame Data")
    print("=" * 80)

    # gwframe
    try:
        import gwframe

        def gwframe_read():
            return gwframe.read(test_file, channel)

        print("\ngwframe (nanobind):")
        gwframe_read_time, gwframe_data = benchmark_function(
            gwframe_read, "read()", n_iterations_read
        )
        print(f"  Samples read: {len(gwframe_data.array)}")
        print(f"  Sample rate: {gwframe_data.sample_rate} Hz")
        print(f"  Data type: {type(gwframe_data.array)}")

    except ImportError as e:
        print(f"\ngwframe not available: {e}")
        gwframe_read_time = None
    except Exception as e:
        print(f"\nError reading with gwframe: {e}")
        gwframe_read_time = None

    # SWIG bindings
    try:
        import numpy as np
        from LDAStools import frameCPP as swig_framecpp

        def swig_read():
            ifo = swig_framecpp.IFrameFStream(test_file)
            data = ifo.ReadFrProcData(0, channel)
            vect = data.RefData()[0]
            # Get the data as numpy array and ensure it owns its data
            # (like gwpy does with numpy.require(..., requirements=['O']))
            return np.require(vect.GetDataArray(), requirements=["O"])

        print("\nLDAStools.frameCPP (SWIG):")
        swig_read_time, swig_data = benchmark_function(
            swig_read, "ReadFrProcData()", n_iterations_read
        )
        print(f"  Samples read: {len(swig_data)}")
        print(f"  Data type: {type(swig_data)}")

    except ImportError as e:
        print(f"\nLDAStools.frameCPP (SWIG) not available: {e}")
        swig_read_time = None
    except Exception as e:
        print(f"\nError reading with SWIG: {e}")
        import traceback

        traceback.print_exc()
        swig_read_time = None

    # Compare
    if gwframe_read_time and swig_read_time:
        speedup = swig_read_time / gwframe_read_time
        print(f"\n{'=' * 80}")
        print(
            f"Frame Reading Speedup: {speedup:.2f}x {'FASTER' if speedup > 1 else 'SLOWER'}"
        )
        print(f"{'=' * 80}")

    # Verify data matches
    if gwframe_read_time and swig_read_time:
        try:
            import numpy as np

            if np.allclose(gwframe_data.array, swig_data):
                print("\n✓ Data verification: Arrays match!")
            else:
                print("\n✗ Warning: Arrays differ!")
                print(
                    f"  gwframe range: [{gwframe_data.array.min():.3e}, {gwframe_data.array.max():.3e}]"
                )
                print(f"  SWIG range: [{swig_data.min():.3e}, {swig_data.max():.3e}]")
        except Exception as e:
            print(f"\n✗ Could not verify data: {e}")

    # ========================================================================
    # Summary
    # ========================================================================
    print("\n\n" + "=" * 80)
    print(f"READ SUMMARY - {file_label}")
    print("=" * 80)

    results = {}
    if gwframe_toc_time and swig_toc_time:
        toc_speedup = swig_toc_time / gwframe_toc_time
        print(
            f"TOC Reading:     gwframe is {toc_speedup:.2f}x {'FASTER' if toc_speedup > 1 else 'SLOWER'} than SWIG"
        )
        results["toc_speedup"] = toc_speedup

    if gwframe_read_time and swig_read_time:
        read_speedup = swig_read_time / gwframe_read_time
        print(
            f"Frame Reading:   gwframe is {read_speedup:.2f}x {'FASTER' if read_speedup > 1 else 'SLOWER'} than SWIG"
        )
        results["read_speedup"] = read_speedup

    print("=" * 80)

    return results


def benchmark_write():
    """Benchmark write performance with realistic file sizes."""
    print("\n\n" + "=" * 80)
    print("Write Benchmark: High-Level API")
    print("=" * 80)
    print(f"Test file: {TEST_FILE_SMALL} (32s)")
    print(f"Channel: {CHANNEL_SMALL}")
    print(f"Iterations: {N_ITERATIONS_WRITE}")
    print()

    # First, read the data using gwframe (32s file)
    print(f"Reading test file: {TEST_FILE_SMALL}")
    import gwframe

    # Resolve path
    repo_root = Path(__file__).parent.parent.parent
    test_file = repo_root / TEST_FILE_SMALL

    result = gwframe.read(str(test_file), CHANNEL_SMALL)
    data = result.array
    t0 = result.t0
    dt = result.dt
    print(f"  Data shape: {data.shape}")
    print(f"  Data size: {data.nbytes / 1024 / 1024:.2f} MB")
    print(f"  Sample rate: {1 / dt:.0f} Hz")
    print(f"  Duration: {len(data) * dt:.1f} seconds")

    # Benchmark gwframe (nanobind)
    print(f"\n{'=' * 80}")
    print("Benchmarking gwframe (nanobind) write")
    print("=" * 80)

    times_nb = []
    for i in range(N_ITERATIONS_WRITE):
        start = time.perf_counter()
        gwframe.write(
            f"/tmp/test_nb_{i}.gwf",
            data,
            t0=t0,
            sample_rate=1.0 / dt,
            name="L1:TEST-STRAIN",
            unit="strain",
        )
        elapsed = time.perf_counter() - start
        times_nb.append(elapsed)
        if i == 0:
            print(f"  Iteration {i + 1}: {elapsed * 1000:.2f} ms")

    times_nb = times_nb[1:]  # Remove warmup
    avg_nb = np.mean(times_nb) * 1000
    std_nb = np.std(times_nb) * 1000
    print("\nResults (after warmup):")
    print(f"  Mean: {avg_nb:.2f} ms")
    print(f"  Std:  {std_nb:.2f} ms")
    print(f"  Throughput: {data.nbytes / np.mean(times_nb) / 1024 / 1024:.1f} MB/s")

    # Benchmark SWIG
    print(f"\n{'=' * 80}")
    print("Benchmarking LDAStools.frameCPP (SWIG) write")
    print("=" * 80)

    try:
        from LDAStools import frameCPP as frcpp

        times_swig = []
        for i in range(N_ITERATIONS_WRITE):
            start = time.perf_counter()

            # Build frame using SWIG API
            frame = frcpp.FrameH()
            frame.SetName("L1")
            frame.SetGTime(frcpp.GPSTime(int(t0), 0))
            frame.SetDt(len(data) * dt)
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
                len(data) * dt,
                0.0,
                0.0,
                0.0,
                0.0,
            )
            frdata.AppendData(vect)
            frame.AppendFrProcData(frdata)
            frame.Write(frcpp.OFrameFStream(f"/tmp/test_swig_{i}.gwf"))

            elapsed = time.perf_counter() - start
            times_swig.append(elapsed)
            if i == 0:
                print(f"  Iteration {i + 1}: {elapsed * 1000:.2f} ms")

        times_swig = times_swig[1:]  # Remove warmup
        avg_swig = np.mean(times_swig) * 1000
        std_swig = np.std(times_swig) * 1000
        print("\nResults (after warmup):")
        print(f"  Mean: {avg_swig:.2f} ms")
        print(f"  Std:  {std_swig:.2f} ms")
        print(
            f"  Throughput: {data.nbytes / np.mean(times_swig) / 1024 / 1024:.1f} MB/s"
        )

        # Compare
        print(f"\n{'=' * 80}")
        print("WRITE SUMMARY")
        print("=" * 80)
        print(f"Nanobind: {avg_nb:.2f} ms (±{std_nb:.2f})")
        print(f"SWIG:     {avg_swig:.2f} ms (±{std_swig:.2f})")
        if avg_swig < avg_nb:
            ratio = avg_nb / avg_swig
            print(f"\nSWIG is {ratio:.2f}x faster")
        else:
            ratio = avg_swig / avg_nb
            print(f"\nNanobind is {ratio:.2f}x faster")

        # Show absolute difference
        print(f"Absolute difference: {abs(avg_nb - avg_swig):.2f} ms")
        print("=" * 80)

        return {"write_speedup": ratio if avg_swig < avg_nb else 1 / ratio}

    except ImportError as e:
        print(f"\nLDAStools.frameCPP (SWIG) not available: {e}")
        return {}


def main():
    # Resolve paths relative to repo root
    repo_root = Path(__file__).parent.parent.parent
    test_file_small = repo_root / TEST_FILE_SMALL
    test_file_large = repo_root / TEST_FILE_LARGE

    # Check files exist
    if not test_file_small.exists():
        print(f"Error: Test file '{test_file_small}' not found")
        sys.exit(1)
    if not test_file_large.exists():
        print(f"Error: Test file '{test_file_large}' not found")
        sys.exit(1)

    print("=" * 80)
    print("Comprehensive Performance Benchmark")
    print("gwframe (nanobind) vs LDAStools.frameCPP (SWIG)")
    print("=" * 80)

    # Benchmark small file read (32s)
    small_results = benchmark_read_file(
        str(test_file_small),
        CHANNEL_SMALL,
        N_ITERATIONS_TOC,
        N_ITERATIONS_READ_SMALL,
        file_label="Small File (32 seconds, 512K samples @ 16kHz)",
    )

    # Benchmark large file read (4096s)
    large_results = benchmark_read_file(
        str(test_file_large),
        CHANNEL_LARGE,
        N_ITERATIONS_TOC,
        N_ITERATIONS_READ_LARGE,
        file_label="Large File (4096 seconds, 65.5M samples @ 16kHz, 489 MB)",
    )

    # Benchmark write
    write_results = benchmark_write()

    # Overall summary
    print("\n\n" + "=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)

    print("\nRead Performance:")
    print("  Small File (32s @ 16kHz):")
    if "toc_speedup" in small_results:
        print(f"    TOC:   {small_results['toc_speedup']:.2f}x")
    if "read_speedup" in small_results:
        print(f"    Read:  {small_results['read_speedup']:.2f}x")

    print("  Large File (4096s @ 16kHz, 489 MB):")
    if "toc_speedup" in large_results:
        print(f"    TOC:   {large_results['toc_speedup']:.2f}x")
    if "read_speedup" in large_results:
        print(f"    Read:  {large_results['read_speedup']:.2f}x")

    print("\nWrite Performance:")
    if "write_speedup" in write_results:
        print(f"  High-level API: {write_results['write_speedup']:.2f}x")

    print("=" * 80)


if __name__ == "__main__":
    main()
