#!/usr/bin/env python3
"""
Quick smoke test: single read/write/inspect for gwframe vs SWIG
to check for obvious regressions before running full benchmarks.
"""

import time

import numpy as np

# Test file
TEST_FILE = "H-H1_GWOSC_O4a_16KHZ_R1-1381289984-4096.gwf"
CHANNEL = "H1:GWOSC-16KHZ_R1_STRAIN"

print("=" * 80)
print("SMOKE TEST: Quick Performance Check")
print("=" * 80)
print(f"File: {TEST_FILE}")
print(f"Channel: {CHANNEL}")
print()

# ============================================================================
# Test 1: Inspection (get_channels)
# ============================================================================
print("=" * 80)
print("Test 1: Inspection (get_channels)")
print("=" * 80)

# gwframe
try:
    import gwframe

    start = time.perf_counter()
    channels_gw = gwframe.get_channels(TEST_FILE)
    time_gw_inspect = time.perf_counter() - start

    print("\ngwframe:")
    print(f"  Time: {time_gw_inspect * 1000:.2f} ms")
    print(f"  Channels: {len(channels_gw)} total")
except Exception as e:
    print(f"\ngwframe FAILED: {e}")
    time_gw_inspect = None

# SWIG
try:
    from LDAStools import frameCPP as frcpp

    start = time.perf_counter()
    ifo = frcpp.IFrameFStream(TEST_FILE)
    toc = ifo.GetTOC()
    adc = list(toc.GetADC())
    proc = list(toc.GetProc())
    sim = list(toc.GetSim())
    time_swig_inspect = time.perf_counter() - start

    print("\nSWIG:")
    print(f"  Time: {time_swig_inspect * 1000:.2f} ms")
    print(f"  Channels: {len(adc) + len(proc) + len(sim)} total")
except Exception as e:
    print(f"\nSWIG FAILED: {e}")
    time_swig_inspect = None

if time_gw_inspect and time_swig_inspect:
    ratio = time_swig_inspect / time_gw_inspect
    print(
        f"\n{'Result:':<20s} gwframe is {ratio:.2f}x {'FASTER' if ratio > 1 else 'SLOWER'}"
    )

# ============================================================================
# Test 2: Read Small (32s slice)
# ============================================================================
print("\n" + "=" * 80)
print("Test 2: Read Small (32s slice)")
print("=" * 80)

# gwframe
try:
    import gwframe

    start = time.perf_counter()
    data_gw = gwframe.read(TEST_FILE, CHANNEL, start=1381289984.0, end=1381290016.0)
    time_gw_read_small = time.perf_counter() - start

    print("\ngwframe:")
    print(f"  Time: {time_gw_read_small * 1000:.2f} ms")
    print(f"  Samples: {len(data_gw.array)}")
    print(f"  Size: {data_gw.array.nbytes / 1024 / 1024:.2f} MB")
except Exception as e:
    print(f"\ngwframe FAILED: {e}")
    time_gw_read_small = None

# SWIG
try:
    from LDAStools import frameCPP as frcpp

    start = time.perf_counter()
    ifo = frcpp.IFrameFStream(TEST_FILE)
    frdata = ifo.ReadFrProcData(0, CHANNEL)
    vect = frdata.RefData()[0]
    data_swig = np.require(vect.GetDataArray(), requirements=["O"])
    # Slice to match gwframe (first 32s)
    data_swig = data_swig[:512000]
    time_swig_read_small = time.perf_counter() - start

    print("\nSWIG:")
    print(f"  Time: {time_swig_read_small * 1000:.2f} ms")
    print(f"  Samples: {len(data_swig)}")
    print(f"  Size: {data_swig.nbytes / 1024 / 1024:.2f} MB")
except Exception as e:
    print(f"\nSWIG FAILED: {e}")
    time_swig_read_small = None

if time_gw_read_small and time_swig_read_small:
    ratio = time_swig_read_small / time_gw_read_small
    print(
        f"\n{'Result:':<20s} gwframe is {ratio:.2f}x {'FASTER' if ratio > 1 else 'SLOWER'}"
    )

# ============================================================================
# Test 3: Read Large (full 4096s file)
# ============================================================================
print("\n" + "=" * 80)
print("Test 3: Read Large (full 4096s file)")
print("=" * 80)

# gwframe
try:
    import gwframe

    start = time.perf_counter()
    data_gw_large = gwframe.read(TEST_FILE, CHANNEL)
    time_gw_read_large = time.perf_counter() - start

    print("\ngwframe:")
    print(f"  Time: {time_gw_read_large * 1000:.2f} ms")
    print(f"  Samples: {len(data_gw_large.array)}")
    print(f"  Size: {data_gw_large.array.nbytes / 1024 / 1024:.2f} MB")
except Exception as e:
    print(f"\ngwframe FAILED: {e}")
    time_gw_read_large = None

# SWIG
try:
    from LDAStools import frameCPP as frcpp

    start = time.perf_counter()
    ifo = frcpp.IFrameFStream(TEST_FILE)
    frdata = ifo.ReadFrProcData(0, CHANNEL)
    vect = frdata.RefData()[0]
    data_swig_large = np.require(vect.GetDataArray(), requirements=["O"])
    time_swig_read_large = time.perf_counter() - start

    print("\nSWIG:")
    print(f"  Time: {time_swig_read_large * 1000:.2f} ms")
    print(f"  Samples: {len(data_swig_large)}")
    print(f"  Size: {data_swig_large.nbytes / 1024 / 1024:.2f} MB")
except Exception as e:
    print(f"\nSWIG FAILED: {e}")
    time_swig_read_large = None

if time_gw_read_large and time_swig_read_large:
    ratio = time_swig_read_large / time_gw_read_large
    print(
        f"\n{'Result:':<20s} gwframe is {ratio:.2f}x {'FASTER' if ratio > 1 else 'SLOWER'}"
    )

# ============================================================================
# Test 4: Write (using 32s slice data)
# ============================================================================
print("\n" + "=" * 80)
print("Test 4: Write (32s of data)")
print("=" * 80)

if "data_gw" in locals():
    write_data = data_gw.array
    write_t0 = data_gw.t0
    write_dt = data_gw.dt

    # gwframe
    try:
        import gwframe

        start = time.perf_counter()
        gwframe.write(
            "/tmp/smoke_test_gw.gwf",
            write_data,
            t0=write_t0,
            sample_rate=1.0 / write_dt,
            name="H1:TEST",
            unit="strain",
        )
        time_gw_write = time.perf_counter() - start

        print("\ngwframe:")
        print(f"  Time: {time_gw_write * 1000:.2f} ms")
        print(
            f"  Throughput: {write_data.nbytes / time_gw_write / 1024 / 1024:.1f} MB/s"
        )
    except Exception as e:
        print(f"\ngwframe FAILED: {e}")
        time_gw_write = None

    # SWIG
    try:
        from LDAStools import frameCPP as frcpp

        GPS_TIME = int(write_t0)
        DURATION = len(write_data) * write_dt

        start = time.perf_counter()
        frame = frcpp.FrameH()
        frame.SetName("H1")
        frame.SetGTime(frcpp.GPSTime(GPS_TIME, 0))
        frame.SetDt(DURATION)
        frame.SetRun(-1)

        dim = frcpp.Dimension(len(write_data), write_dt, "s", 0.0)
        vect = frcpp.FrVect("H1:TEST", frcpp.FrVect.FR_VECT_8R, 1, dim, "")
        vect.GetDataArray()[:] = write_data

        frdata = frcpp.FrProcData(
            "H1:TEST",
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
        frame.Write(frcpp.OFrameFStream("/tmp/smoke_test_swig.gwf"))
        time_swig_write = time.perf_counter() - start

        print("\nSWIG:")
        print(f"  Time: {time_swig_write * 1000:.2f} ms")
        print(
            f"  Throughput: {write_data.nbytes / time_swig_write / 1024 / 1024:.1f} MB/s"
        )
    except Exception as e:
        print(f"\nSWIG FAILED: {e}")
        time_swig_write = None

    if time_gw_write and time_swig_write:
        ratio = time_swig_write / time_gw_write
        print(
            f"\n{'Result:':<20s} gwframe is {ratio:.2f}x {'FASTER' if ratio > 1 else 'SLOWER'}"
        )
else:
    print("\nSkipping write test (no data available)")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("SMOKE TEST SUMMARY")
print("=" * 80)

results = []
if time_gw_inspect and time_swig_inspect:
    ratio = time_swig_inspect / time_gw_inspect
    results.append(("Inspection", ratio))

if time_gw_read_small and time_swig_read_small:
    ratio = time_swig_read_small / time_gw_read_small
    results.append(("Read Small (32s)", ratio))

if time_gw_read_large and time_swig_read_large:
    ratio = time_swig_read_large / time_gw_read_large
    results.append(("Read Large (4096s)", ratio))

if time_gw_write and time_swig_write:
    ratio = time_swig_write / time_gw_write
    results.append(("Write (32s)", ratio))

if results:
    print("\nPerformance (gwframe relative to SWIG):")
    print("-" * 80)
    for name, ratio in results:
        status = "✓" if ratio >= 0.8 else "⚠"
        faster = "FASTER" if ratio > 1 else "SLOWER"
        print(f"  {status} {name:<25s} {ratio:.2f}x {faster}")

    # Check for regressions
    print("\nRegression Check:")
    print("-" * 80)
    any_regression = False
    for name, ratio in results:
        if ratio < 0.8:  # More than 20% slower
            print(f"  ⚠ POTENTIAL REGRESSION in {name}: {ratio:.2f}x")
            any_regression = True

    if not any_regression:
        print("  ✓ No significant regressions detected")
        print("  ✓ Ready to run full benchmarks with multiple iterations")
    else:
        print("  ⚠ Consider profiling with py-spy before full benchmarks")
else:
    print("\nNo comparison results available")

print("=" * 80)
