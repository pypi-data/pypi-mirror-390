"""Test time-based slicing for read() function."""

import numpy as np
import pytest

import gwframe


def test_create_multiframe_file(tmp_path):
    """Test creating multi-frame file for testing."""
    t0_base = 1234567890.0
    duration_per_frame = 1.0
    sample_rate = 16384.0
    n_samples = int(duration_per_frame * sample_rate)
    n_frames = 5

    tmp_file = tmp_path / "test.gwf"

    with gwframe.FrameWriter(str(tmp_file)) as writer:
        for i in range(n_frames):
            t0 = t0_base + i * duration_per_frame
            data = np.full(n_samples, float(i), dtype=np.float64)
            writer.write(
                data, t0=t0, sample_rate=sample_rate, name="L1:TEST", unit="counts"
            )

    # Verify file was created
    assert tmp_file.exists()


def test_read_exact_single_frame(tmp_path):
    """Test reading exact single frame with time slicing."""
    t0_base = 1234567890.0
    duration_per_frame = 1.0
    sample_rate = 16384.0
    n_samples = int(duration_per_frame * sample_rate)
    n_frames = 5

    tmp_file = tmp_path / "test.gwf"

    with gwframe.FrameWriter(str(tmp_file)) as writer:
        for i in range(n_frames):
            t0 = t0_base + i * duration_per_frame
            data = np.full(n_samples, float(i), dtype=np.float64)
            writer.write(
                data, t0=t0, sample_rate=sample_rate, name="L1:TEST", unit="counts"
            )

    # Read exact single frame
    frame_idx = 2
    start = t0_base + frame_idx * duration_per_frame
    end = start + duration_per_frame

    data_time = gwframe.read(str(tmp_file), "L1:TEST", start=start, end=end)

    assert abs(data_time.t0 - start) < 1e-9
    assert abs(data_time.duration - duration_per_frame) < 1e-9
    assert len(np.unique(data_time.array)) == 1
    assert np.unique(data_time.array)[0] == float(frame_idx)


def test_read_partial_frame(tmp_path):
    """Test reading partial frame (middle portion)."""
    t0_base = 1234567890.0
    duration_per_frame = 1.0
    sample_rate = 16384.0
    n_samples = int(duration_per_frame * sample_rate)
    n_frames = 5

    tmp_file = tmp_path / "test.gwf"

    with gwframe.FrameWriter(str(tmp_file)) as writer:
        for i in range(n_frames):
            t0 = t0_base + i * duration_per_frame
            data = np.full(n_samples, float(i), dtype=np.float64)
            writer.write(
                data, t0=t0, sample_rate=sample_rate, name="L1:TEST", unit="counts"
            )

    start = t0_base + 0.25
    end = t0_base + 0.75
    expected_duration = end - start
    expected_samples = int(expected_duration * sample_rate)

    data_partial = gwframe.read(str(tmp_file), "L1:TEST", start=start, end=end)

    assert abs(len(data_partial.array) - expected_samples) <= 1


def test_read_spanning_multiple_frames(tmp_path):
    """Test reading spanning multiple frames."""
    t0_base = 1234567890.0
    duration_per_frame = 1.0
    sample_rate = 16384.0
    n_samples = int(duration_per_frame * sample_rate)
    n_frames = 5

    tmp_file = tmp_path / "test.gwf"

    with gwframe.FrameWriter(str(tmp_file)) as writer:
        for i in range(n_frames):
            t0 = t0_base + i * duration_per_frame
            data = np.full(n_samples, float(i), dtype=np.float64)
            writer.write(
                data, t0=t0, sample_rate=sample_rate, name="L1:TEST", unit="counts"
            )

    start = t0_base + 1.5
    end = t0_base + 3.5
    expected_duration = end - start
    expected_samples = int(expected_duration * sample_rate)

    data_span = gwframe.read(str(tmp_file), "L1:TEST", start=start, end=end)

    # Should contain data from frames 1, 2, and 3
    unique_values = set(np.unique(data_span.array))
    expected_values = {1.0, 2.0, 3.0}

    assert unique_values == expected_values
    assert abs(len(data_span.array) - expected_samples) <= 2


def test_read_entire_time_range(tmp_path):
    """Test reading entire time range."""
    t0_base = 1234567890.0
    duration_per_frame = 1.0
    sample_rate = 16384.0
    n_samples = int(duration_per_frame * sample_rate)
    n_frames = 5

    tmp_file = tmp_path / "test.gwf"

    with gwframe.FrameWriter(str(tmp_file)) as writer:
        for i in range(n_frames):
            t0 = t0_base + i * duration_per_frame
            data = np.full(n_samples, float(i), dtype=np.float64)
            writer.write(
                data, t0=t0, sample_rate=sample_rate, name="L1:TEST", unit="counts"
            )

    start = t0_base
    end = t0_base + n_frames * duration_per_frame

    data_all = gwframe.read(str(tmp_file), "L1:TEST", start=start, end=end)

    expected_total_samples = n_frames * n_samples
    assert abs(len(data_all.array) - expected_total_samples) <= n_frames


def test_parameter_validation(tmp_path):
    """Test parameter validation."""
    tmp_file = tmp_path / "test.gwf"

    # Create minimal test file
    with gwframe.FrameWriter(str(tmp_file)) as writer:
        data = np.random.randn(16384)
        writer.write(
            data, t0=1234567890.0, sample_rate=16384, name="L1:TEST", unit="counts"
        )

    # Test: start without end
    with pytest.raises(ValueError, match="together"):
        gwframe.read(str(tmp_file), "L1:TEST", start=1234567890.0)

    # Test: end without start
    with pytest.raises(ValueError, match="together"):
        gwframe.read(str(tmp_file), "L1:TEST", end=1234567891.0)

    # Test: start/end with frame_index
    with pytest.raises(ValueError, match="mutually exclusive"):
        gwframe.read(
            str(tmp_file),
            "L1:TEST",
            frame_index=1,
            start=1234567890.0,
            end=1234567891.0,
        )


def test_read_bytes_multi_channel_time_slicing(tmp_path):
    """Test reading multiple channels with time slicing from bytes."""
    # Create multi-frame file with multiple channels
    tmp_file = tmp_path / "multi_channel_multi_frame.gwf"
    t0_base = 1234567890.0
    duration_per_frame = 1.0
    sample_rate = 16384.0
    n_samples = int(duration_per_frame * sample_rate)
    n_frames = 3

    with gwframe.FrameWriter(str(tmp_file)) as writer:
        for i in range(n_frames):
            t0 = t0_base + i * duration_per_frame
            channels = {
                "L1:CHAN1": np.full(n_samples, float(i), dtype=np.float64),
                "L1:CHAN2": np.full(n_samples, float(i * 2), dtype=np.float64),
            }
            writer.write(channels, t0=t0, sample_rate=sample_rate, name="L1")

    # Read from bytes with time slicing across multiple frames
    with open(tmp_file, "rb") as f:
        gwf_bytes = f.read()

    start = t0_base + 0.5
    end = t0_base + 2.5

    # Read all channels with time slicing
    result = gwframe.read_bytes(gwf_bytes, channel=None, start=start, end=end)

    assert isinstance(result, dict)
    assert "L1:CHAN1" in result
    assert "L1:CHAN2" in result

    # Verify both channels were sliced correctly
    for _ch, ts in result.items():
        assert ts.t0 >= start
        assert ts.t0 + ts.duration <= end + 1 / sample_rate  # Allow rounding
        assert len(ts.array) > 0


def test_read_bytes_channel_list_time_slicing(tmp_path):
    """Test reading specific channel list with time slicing from bytes."""
    tmp_file = tmp_path / "multi_channel.gwf"
    t0_base = 1234567890.0
    duration_per_frame = 1.0
    sample_rate = 16384.0
    n_samples = int(duration_per_frame * sample_rate)
    n_frames = 3

    with gwframe.FrameWriter(str(tmp_file)) as writer:
        for i in range(n_frames):
            t0 = t0_base + i * duration_per_frame
            channels = {
                "L1:CHAN1": np.full(n_samples, float(i)),
                "L1:CHAN2": np.full(n_samples, float(i * 2)),
                "L1:CHAN3": np.full(n_samples, float(i * 3)),
            }
            writer.write(channels, t0=t0, sample_rate=sample_rate, name="L1")

    with open(tmp_file, "rb") as f:
        gwf_bytes = f.read()

    # Read only specific channels with time slicing
    channel_list = ["L1:CHAN1", "L1:CHAN3"]
    start = t0_base + 0.5
    end = t0_base + 2.5

    result = gwframe.read_bytes(gwf_bytes, channel=channel_list, start=start, end=end)

    assert isinstance(result, dict)
    assert set(result.keys()) == set(channel_list)
    assert "L1:CHAN2" not in result  # Should not include unspecified channel
