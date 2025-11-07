"""Comprehensive tests for gwframe read functionality."""

from io import BytesIO

import numpy as np
import pytest

import gwframe


class TestReadSingleChannel:
    """Tests for reading single channels."""

    def test_read_from_file_path(self, test_gwf_file):
        """Test reading single channel from file path."""
        data = gwframe.read(str(test_gwf_file), "L1:GWOSC-16KHZ_R1_STRAIN")

        assert isinstance(data, gwframe.TimeSeries)
        assert data.name == "L1:GWOSC-16KHZ_R1_STRAIN"
        assert len(data.array) > 0
        assert data.sample_rate > 0
        assert data.t0 > 0

    def test_read_from_file_object(self, test_gwf_file):
        """Test reading single channel from file object."""
        with open(test_gwf_file, "rb") as f:
            data = gwframe.read(f, "L1:GWOSC-16KHZ_R1_STRAIN")

        assert isinstance(data, gwframe.TimeSeries)
        assert len(data.array) > 0

    def test_read_from_bytesio(self, test_gwf_file):
        """Test reading single channel from BytesIO."""
        with open(test_gwf_file, "rb") as f:
            gwf_bytes = f.read()

        data = gwframe.read(BytesIO(gwf_bytes), "L1:GWOSC-16KHZ_R1_STRAIN")

        assert isinstance(data, gwframe.TimeSeries)
        assert len(data.array) > 0

    def test_read_bytes_function(self, test_gwf_file):
        """Test read_bytes() function."""
        with open(test_gwf_file, "rb") as f:
            gwf_bytes = f.read()

        data = gwframe.read_bytes(gwf_bytes, "L1:GWOSC-16KHZ_R1_STRAIN")

        assert isinstance(data, gwframe.TimeSeries)
        assert len(data.array) > 0

    def test_read_nonexistent_channel(self, test_gwf_file):
        """Test reading non-existent channel raises ChannelNotFoundError."""
        with pytest.raises(gwframe.ChannelNotFoundError) as exc_info:
            gwframe.read(str(test_gwf_file), "NONEXISTENT:CHANNEL")

        # Verify error has helpful attributes
        err = exc_info.value
        assert err.channels == ["NONEXISTENT:CHANNEL"]
        assert len(err.available_channels) > 0
        assert "NONEXISTENT:CHANNEL" in str(err)
        assert "Available channels" in str(err)

    def test_read_nonexistent_file(self):
        """Test reading non-existent file raises error."""
        with pytest.raises(RuntimeError):
            gwframe.read("/nonexistent/file.gwf", "L1:STRAIN")


class TestReadMultiChannel:
    """Tests for reading multiple channels."""

    def test_read_all_channels(self, test_gwf_file):
        """Test reading all channels with channel=None."""
        all_data = gwframe.read(str(test_gwf_file), channel=None)

        assert isinstance(all_data, dict)
        assert len(all_data) > 0
        for ch, ts in all_data.items():
            assert isinstance(ch, str)
            assert isinstance(ts, gwframe.TimeSeries)
            assert len(ts.array) > 0

    def test_read_channel_list(self, test_gwf_file):
        """Test reading specific list of channels."""
        # Get all channels first
        all_channels = gwframe.read(str(test_gwf_file), channel=None)
        channel_list = list(all_channels.keys())[:2]

        # Read subset
        data_dict = gwframe.read(str(test_gwf_file), channel_list)

        assert isinstance(data_dict, dict)
        assert len(data_dict) == len(channel_list)
        for ch in channel_list:
            assert ch in data_dict
            assert isinstance(data_dict[ch], gwframe.TimeSeries)

    def test_read_all_channels_from_bytes(self, test_gwf_file):
        """Test reading all channels from bytes."""
        with open(test_gwf_file, "rb") as f:
            gwf_bytes = f.read()

        all_data = gwframe.read_bytes(gwf_bytes, channel=None)

        assert isinstance(all_data, dict)
        assert len(all_data) > 0

    def test_read_channel_list_from_file_object(self, test_gwf_file):
        """Test reading channel list from file object."""
        # Get channel names first
        all_channels = gwframe.read(str(test_gwf_file), channel=None)
        channel_list = [next(iter(all_channels.keys()))]

        # Read from file object
        with open(test_gwf_file, "rb") as f:
            data_dict = gwframe.read(f, channel_list)

        assert isinstance(data_dict, dict)
        assert len(data_dict) == 1


class TestChecksumValidation:
    """Tests for checksum validation."""

    def test_read_without_validation_default(self, test_gwf_file):
        """Test reading without validation (default)."""
        data = gwframe.read(str(test_gwf_file), "L1:GWOSC-16KHZ_R1_STRAIN")
        assert len(data.array) > 0

    def test_read_with_validation_enabled(self, test_gwf_file):
        """Test reading with validation enabled."""
        data = gwframe.read(
            str(test_gwf_file), "L1:GWOSC-16KHZ_R1_STRAIN", validate_checksum=True
        )
        assert len(data.array) > 0

    def test_read_bytes_with_validation(self, test_gwf_file):
        """Test read_bytes() with validation."""
        with open(test_gwf_file, "rb") as f:
            gwf_bytes = f.read()

        data = gwframe.read_bytes(
            gwf_bytes, "L1:GWOSC-16KHZ_R1_STRAIN", validate_checksum=True
        )
        assert len(data.array) > 0

    def test_read_file_object_with_validation(self, test_gwf_file):
        """Test reading from file object with validation."""
        with open(test_gwf_file, "rb") as f:
            data = gwframe.read(f, "L1:GWOSC-16KHZ_R1_STRAIN", validate_checksum=True)
        assert len(data.array) > 0


class TestFrameIndex:
    """Tests for frame index parameter."""

    def test_read_specific_frame_index(self, tmp_path):
        """Test reading specific frame by index."""
        # Create multi-frame file
        tmp_file = tmp_path / "multiframe.gwf"
        with gwframe.FrameWriter(str(tmp_file)) as writer:
            for i in range(3):
                data = np.full(1000, float(i))
                writer.write(
                    data,
                    t0=1234567890.0 + i,
                    sample_rate=1000,
                    name="L1:TEST",
                    unit="counts",
                )

        # Read different frames
        data0 = gwframe.read(str(tmp_file), "L1:TEST", frame_index=0)
        data1 = gwframe.read(str(tmp_file), "L1:TEST", frame_index=1)
        data2 = gwframe.read(str(tmp_file), "L1:TEST", frame_index=2)

        assert np.all(data0.array == 0.0)
        assert np.all(data1.array == 1.0)
        assert np.all(data2.array == 2.0)

    def test_read_invalid_frame_index(self, tmp_path):
        """Test reading invalid frame index raises error."""
        tmp_file = tmp_path / "single_frame.gwf"
        with gwframe.FrameWriter(str(tmp_file)) as writer:
            data = np.random.randn(1000)
            writer.write(
                data,
                t0=1234567890.0,
                sample_rate=1000,
                name="L1:TEST",
                unit="counts",
            )

        with pytest.raises((IndexError, RuntimeError, ValueError)):
            gwframe.read(str(tmp_file), "L1:TEST", frame_index=10)


class TestNumpyIntegration:
    """Tests for numpy array handling."""

    def test_array_is_numpy_array(self, test_gwf_file):
        """Test that returned data is numpy array."""
        data = gwframe.read(str(test_gwf_file), "L1:GWOSC-16KHZ_R1_STRAIN")
        assert isinstance(data.array, np.ndarray)

    def test_array_dtype(self, test_gwf_file):
        """Test array dtype is correct."""
        data = gwframe.read(str(test_gwf_file), "L1:GWOSC-16KHZ_R1_STRAIN")
        # Should be float64 for real data
        assert data.array.dtype in (np.float64, np.float32)

    def test_timeseries_metadata(self, test_gwf_file):
        """Test TimeSeries metadata fields."""
        data = gwframe.read(str(test_gwf_file), "L1:GWOSC-16KHZ_R1_STRAIN")

        assert hasattr(data, "array")
        assert hasattr(data, "t0")
        assert hasattr(data, "dt")
        assert hasattr(data, "duration")
        assert hasattr(data, "sample_rate")
        assert hasattr(data, "name")
        assert hasattr(data, "unit")

        # Verify consistency
        assert abs(data.duration - len(data.array) * data.dt) < 1e-9
        assert abs(data.sample_rate - 1.0 / data.dt) < 1e-9


def test_read_bytes_type_validation(tmp_path):
    """Test that read_bytes validates input is bytes."""
    tmp_file = tmp_path / "test.gwf"
    with gwframe.FrameWriter(str(tmp_file)) as writer:
        writer.write(
            np.random.randn(1000),
            t0=1234567890.0,
            sample_rate=1000,
            name="L1:TEST",
        )

    # Should raise TypeError for non-bytes input
    with pytest.raises(TypeError, match="data must be bytes"):
        gwframe.read_bytes("not_bytes", "L1:TEST")


def test_read_bytes_start_end_validation(tmp_path):
    """Test validation of start/end parameter combinations in read_bytes."""
    tmp_file = tmp_path / "test.gwf"
    with gwframe.FrameWriter(str(tmp_file)) as writer:
        writer.write(
            np.random.randn(1000),
            t0=1234567890.0,
            sample_rate=1000,
            name="L1:TEST",
        )

    with open(tmp_file, "rb") as f:
        gwf_bytes = f.read()

    # start without end should raise
    with pytest.raises(ValueError, match="start and end must be specified together"):
        gwframe.read_bytes(gwf_bytes, "L1:TEST", start=1234567890.0)

    # end without start should raise
    with pytest.raises(ValueError, match="start and end must be specified together"):
        gwframe.read_bytes(gwf_bytes, "L1:TEST", end=1234567891.0)


def test_read_bytes_start_end_mutually_exclusive_with_frame_index(tmp_path):
    """Test that start/end cannot be used with frame_index in read_bytes."""
    tmp_file = tmp_path / "test.gwf"
    with gwframe.FrameWriter(str(tmp_file)) as writer:
        writer.write(
            np.random.randn(1000),
            t0=1234567890.0,
            sample_rate=1000,
            name="L1:TEST",
        )

    with open(tmp_file, "rb") as f:
        gwf_bytes = f.read()

    with pytest.raises(ValueError, match="mutually exclusive"):
        gwframe.read_bytes(
            gwf_bytes,
            "L1:TEST",
            frame_index=1,
            start=1234567890.0,
            end=1234567891.0,
        )


def test_invalid_time_range_error(tmp_path):
    """Test InvalidTimeRangeError is raised for out-of-range time requests."""
    # Create a test file with known time range
    tmp_file = tmp_path / "test.gwf"
    with gwframe.FrameWriter(str(tmp_file)) as writer:
        writer.write(
            np.array([1.0, 2.0, 3.0]),
            t0=1234567890.0,  # File starts at this GPS time
            sample_rate=1,  # 3 samples at 1 Hz = 3 seconds duration
            name="L1:TEST",
            unit="counts",
        )

    # Try to read time range completely after file end
    with pytest.raises(gwframe.InvalidTimeRangeError) as exc_info:
        gwframe.read(
            str(tmp_file),
            "L1:TEST",
            start=1234567900.0,  # Way after file end
            end=1234567910.0,
        )

    # Verify error has correct attributes
    err = exc_info.value
    assert err.start == 1234567900.0
    assert err.end == 1234567910.0
    assert err.file_start == 1234567890.0
    assert err.file_end == 1234567893.0  # t0 + duration
    assert "does not overlap" in str(err)
    assert "after file end" in str(err)
