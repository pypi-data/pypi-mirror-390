"""Roundtrip tests for writing and reading various data types."""

import numpy as np

import gwframe


def test_complex64_roundtrip(tmp_path):
    """Test complex64 (FR_VECT_8C) write and read."""
    t0 = 1234567890.0
    duration = 1.0
    sample_rate = 16384.0
    n_samples = int(duration * sample_rate)

    tmp_file = tmp_path / "test_c64.gwf"

    # Create complex64 data
    data_c64 = np.exp(1j * 2 * np.pi * np.linspace(0, 1, n_samples)).astype(
        np.complex64
    )

    # Write frame
    frame = gwframe.Frame(t0=t0, duration=duration, name="L1", run=1)
    frame.add_channel(
        "L1:TEST_C64", data_c64, sample_rate=sample_rate, unit="", channel_type="proc"
    )
    frame.write(str(tmp_file))

    # Read back
    ts = gwframe.read(str(tmp_file), "L1:TEST_C64")

    assert ts.array.dtype == np.complex64
    assert np.allclose(ts.array, data_c64)


def test_complex128_roundtrip(tmp_path):
    """Test complex128 (FR_VECT_16C) write and read."""
    t0 = 1234567890.0
    duration = 1.0
    sample_rate = 16384.0
    n_samples = int(duration * sample_rate)

    tmp_file = tmp_path / "test_c128.gwf"

    # Create complex128 data
    data_c128 = np.exp(1j * 2 * np.pi * np.linspace(0, 1, n_samples)).astype(
        np.complex128
    )

    # Write frame
    frame = gwframe.Frame(t0=t0, duration=duration, name="L1", run=1)
    frame.add_channel(
        "L1:TEST_C128",
        data_c128,
        sample_rate=sample_rate,
        unit="",
        channel_type="proc",
    )
    frame.write(str(tmp_file))

    # Read back
    ts = gwframe.read(str(tmp_file), "L1:TEST_C128")

    assert ts.array.dtype == np.complex128
    assert np.allclose(ts.array, data_c128)


def test_mixed_real_complex_roundtrip(tmp_path):
    """Test mixed real and complex data in same frame."""
    t0 = 1234567890.0
    duration = 1.0
    sample_rate = 16384.0
    n_samples = int(duration * sample_rate)

    tmp_file = tmp_path / "test_mixed.gwf"

    # Create mixed data
    data_real = np.random.randn(n_samples)
    data_complex = (
        np.random.randn(n_samples) + 1j * np.random.randn(n_samples)
    ).astype(np.complex128)

    # Write frame with both types
    frame = gwframe.Frame(t0=t0, duration=duration, name="L1", run=1)
    frame.add_channel(
        "L1:REAL",
        data_real,
        sample_rate=sample_rate,
        unit="strain",
        channel_type="proc",
    )
    frame.add_channel(
        "L1:COMPLEX",
        data_complex,
        sample_rate=sample_rate,
        unit="",
        channel_type="proc",
    )
    frame.write(str(tmp_file))

    # Read back both channels
    ts_real = gwframe.read(str(tmp_file), "L1:REAL")
    ts_complex = gwframe.read(str(tmp_file), "L1:COMPLEX")

    assert ts_real.array.dtype == np.float64
    assert ts_complex.array.dtype == np.complex128
    assert np.allclose(ts_real.array, data_real)
    assert np.allclose(ts_complex.array, data_complex)


def test_integer_dtypes_roundtrip(tmp_path):
    """Test writing and reading various integer data types."""
    t0 = 1234567890.0
    sample_rate = 1000.0
    n_samples = 1000

    tmp_file = tmp_path / "test_int_dtypes.gwf"

    # Create data with different integer dtypes
    channels = {
        "L1:INT16": np.random.randint(-100, 100, n_samples, dtype=np.int16),
        "L1:INT32": np.random.randint(-1000, 1000, n_samples, dtype=np.int32),
        "L1:INT64": np.random.randint(-10000, 10000, n_samples, dtype=np.int64),
        "L1:UINT16": np.random.randint(0, 200, n_samples, dtype=np.uint16),
        "L1:UINT32": np.random.randint(0, 2000, n_samples, dtype=np.uint32),
    }

    # Write all channels
    frame = gwframe.Frame(t0=t0, duration=n_samples / sample_rate, name="L1")
    for ch_name, data in channels.items():
        frame.add_channel(ch_name, data, sample_rate=sample_rate)
    frame.write(str(tmp_file))

    # Read back and verify dtypes are preserved
    for ch_name, original_data in channels.items():
        read_data = gwframe.read(str(tmp_file), ch_name)
        assert read_data.array.dtype == original_data.dtype
        assert len(read_data.array) == len(original_data)
        # For integer types, values should match exactly
        np.testing.assert_array_equal(read_data.array, original_data)


def test_float32_roundtrip(tmp_path):
    """Test writing and reading float32 data."""
    t0 = 1234567890.0
    sample_rate = 1000.0
    n_samples = 1000

    tmp_file = tmp_path / "test_float32.gwf"

    data_f32 = np.random.randn(n_samples).astype(np.float32)

    gwframe.write(
        str(tmp_file),
        data_f32,
        t0=t0,
        sample_rate=sample_rate,
        name="L1:FLOAT32",
    )

    # Read back
    read_data = gwframe.read(str(tmp_file), "L1:FLOAT32")
    assert read_data.array.dtype == np.float32
    np.testing.assert_array_almost_equal(read_data.array, data_f32)


def test_simulated_channel_roundtrip(tmp_path):
    """Test writing and reading simulated channels."""
    tmp_file = tmp_path / "sim_data.gwf"
    data = np.random.randn(1000)

    gwframe.write(
        str(tmp_file),
        data,
        t0=1234567890.0,
        sample_rate=1000,
        name="L1:SIM_STRAIN",
        channel_type="sim",
    )

    # Read back and verify
    read_data = gwframe.read(str(tmp_file), "L1:SIM_STRAIN")
    assert read_data.type == "sim"
    assert len(read_data.array) == len(data)
    np.testing.assert_array_almost_equal(read_data.array, data)


def test_mixed_proc_and_sim_roundtrip(tmp_path):
    """Test file with both processed and simulated channels."""
    tmp_file = tmp_path / "mixed.gwf"
    frame = gwframe.Frame(t0=1234567890.0, duration=1.0, name="L1")

    # Add proc channel
    proc_data = np.random.randn(1000)
    frame.add_channel("L1:PROC_CHAN", proc_data, sample_rate=1000, channel_type="proc")

    # Add sim channel
    sim_data = np.random.randn(1000)
    frame.add_channel("L1:SIM_CHAN", sim_data, sample_rate=1000, channel_type="sim")

    frame.write(str(tmp_file))

    # Read back both channels by name
    proc_result = gwframe.read(str(tmp_file), "L1:PROC_CHAN")
    sim_result = gwframe.read(str(tmp_file), "L1:SIM_CHAN")

    assert proc_result.type == "proc"
    assert sim_result.type == "sim"
    assert len(proc_result.array) == len(proc_data)
    assert len(sim_result.array) == len(sim_data)
