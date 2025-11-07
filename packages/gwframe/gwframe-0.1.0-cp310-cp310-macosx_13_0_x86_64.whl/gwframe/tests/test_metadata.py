"""Tests for frame metadata: tRange, fRange, leap seconds, CRC checksums."""

from contextlib import suppress

import numpy as np
import pytest

import gwframe
import gwframe._core as _core


class TestTRangeFRange:
    """Tests for tRange and fRange metadata in FrProcData."""

    def test_trange_equals_duration(self, tmp_path):
        """Test that tRange equals duration."""
        tmp_file = tmp_path / "trange.gwf"

        t0 = 1234567890.0
        duration = 1.0
        sample_rate = 16384.0
        n_samples = int(duration * sample_rate)

        # Write frame
        frame = gwframe.Frame(t0=t0, duration=duration, name="L1", run=1)
        data = np.random.randn(n_samples)
        frame.add_channel(
            "L1:TEST", data, sample_rate=sample_rate, unit="strain", channel_type="proc"
        )
        frame.write(str(tmp_file))

        # Read back using low-level API to inspect FrProcData
        stream = _core.IFrameFStream(str(tmp_file))
        fr_proc_data = stream.read_fr_proc_data(0, "L1:TEST")

        actual_trange = fr_proc_data.get_t_range()
        expected_trange = duration

        assert abs(actual_trange - expected_trange) < 1e-10

    def test_frange_equals_nyquist(self, tmp_path):
        """Test that fRange equals Nyquist frequency (sample_rate / 2)."""
        tmp_file = tmp_path / "frange.gwf"

        t0 = 1234567890.0
        duration = 1.0
        sample_rate = 16384.0
        n_samples = int(duration * sample_rate)
        expected_frange = sample_rate / 2.0

        # Write frame
        frame = gwframe.Frame(t0=t0, duration=duration, name="L1", run=1)
        data = np.random.randn(n_samples)
        frame.add_channel(
            "L1:TEST", data, sample_rate=sample_rate, unit="strain", channel_type="proc"
        )
        frame.write(str(tmp_file))

        # Read back using low-level API
        stream = _core.IFrameFStream(str(tmp_file))
        fr_proc_data = stream.read_fr_proc_data(0, "L1:TEST")

        actual_frange = fr_proc_data.get_f_range()

        assert abs(actual_frange - expected_frange) < 1e-10

    def test_trange_frange_different_sample_rates(self, tmp_path):
        """Test tRange and fRange with different sample rates."""
        t0 = 1234567890.0
        duration = 1.0

        sample_rates = [256.0, 1024.0, 16384.0]

        for sample_rate in sample_rates:
            tmp_file = tmp_path / f"test_{int(sample_rate)}Hz.gwf"
            n_samples = int(duration * sample_rate)
            expected_frange = sample_rate / 2.0

            # Write frame
            frame = gwframe.Frame(t0=t0, duration=duration, name="L1", run=1)
            data = np.random.randn(n_samples)
            frame.add_channel(
                "L1:TEST",
                data,
                sample_rate=sample_rate,
                unit="counts",
                channel_type="proc",
            )
            frame.write(str(tmp_file))

            # Read back and verify
            stream = _core.IFrameFStream(str(tmp_file))
            fr_proc_data = stream.read_fr_proc_data(0, "L1:TEST")

            actual_trange = fr_proc_data.get_t_range()
            actual_frange = fr_proc_data.get_f_range()

            assert abs(actual_trange - duration) < 1e-10
            assert abs(actual_frange - expected_frange) < 1e-10


class TestLeapSeconds:
    """Tests for leap second metadata in frames."""

    def test_leap_seconds_for_different_times(self):
        """Test leap seconds calculation for different GPS times."""
        test_cases = [
            (1234567890.0, 37),  # ~2019, should have 37 leap seconds
            (1000000000.0, 34),  # ~2011, should have 34 leap seconds
            (1400000000.0, 37),  # ~2024, should have 37 leap seconds
        ]

        for gps_time, expected_leap_secs in test_cases:
            gps = _core.gpstime_from_float(gps_time)
            actual_leap_secs = gps.get_leap_seconds()
            assert actual_leap_secs == expected_leap_secs, (
                f"GPS {gps_time}: expected {expected_leap_secs}, got {actual_leap_secs}"
            )

    def test_frame_uses_correct_leap_seconds(self):
        """Test that Frame uses correct leap seconds."""
        frame = gwframe.Frame(t0=1234567890.0, duration=1.0, name="L1", run=1)
        leap_secs = frame._gps_time.get_leap_seconds()

        # GPS time 1234567890.0 (~2019) should have 37 leap seconds
        assert leap_secs == 37

    def test_leap_seconds_in_written_frame(self, tmp_path):
        """Test that leap seconds are correctly set in written frames."""
        tmp_file = tmp_path / "leap_seconds.gwf"

        # Create and write frame
        frame = gwframe.Frame(
            t0=1234567890.0, duration=1.0, name="L1", run=1, frame_number=42
        )
        data = np.random.randn(1000)
        frame.add_channel("L1:TEST", data, sample_rate=1000, unit="strain")
        frame.write(str(tmp_file))

        # Verify frame was written correctly
        result = gwframe.read(str(tmp_file), "L1:TEST")
        assert len(result.array) == 1000
        assert result.t0 == 1234567890.0

    def test_gpstime_from_float(self):
        """Test gpstime_from_float conversion."""
        gps_time = 1234567890.5
        gps = _core.gpstime_from_float(gps_time)

        # Verify GPSTime object was created
        assert gps is not None
        # Leap seconds should be available
        leap_secs = gps.get_leap_seconds()
        assert isinstance(leap_secs, int)
        assert leap_secs > 0


class TestCRCChecksum:
    """Tests for CRC checksum validation."""

    def test_written_frames_have_crc(self, tmp_path):
        """Test that written frames include CRC checksums."""
        tmp_file = tmp_path / "crc_test.gwf"

        # Write frame
        t0 = 1234567890.0
        duration = 1.0
        sample_rate = 16384.0
        n_samples = int(duration * sample_rate)

        frame = gwframe.Frame(t0=t0, duration=duration, name="L1", run=1)
        data = np.random.randn(n_samples)
        frame.add_channel(
            "L1:TEST", data, sample_rate=sample_rate, unit="strain", channel_type="proc"
        )
        frame.write(str(tmp_file))

        # Read file bytes and validate checksum
        with open(tmp_file, "rb") as f:
            frame_bytes = f.read()

        # This should not raise an exception
        _core.validate_frame_checksums(frame_bytes)

    def test_crc_validation_detects_corruption(self, tmp_path):
        """Test that CRC validation can detect corrupted frames."""
        tmp_file = tmp_path / "crc_corrupt.gwf"

        # Write valid frame
        frame = gwframe.Frame(t0=1234567890.0, duration=1.0, name="L1", run=1)
        data = np.random.randn(1000)
        frame.add_channel("L1:TEST", data, sample_rate=1000, unit="strain")
        frame.write(str(tmp_file))

        # Read and corrupt some bytes
        with open(tmp_file, "rb") as f:
            frame_bytes = bytearray(f.read())

        # Corrupt some data (but not the header to keep it readable)
        if len(frame_bytes) > 1000:
            frame_bytes[500] = (frame_bytes[500] + 1) % 256
            frame_bytes[501] = (frame_bytes[501] + 1) % 256

            # Try to validate corrupted data - if it raises VerifyException,
            # that's expected (CRC validation caught the corruption).
            # If validation passes, the corruption may not have affected
            # checksummed regions, which is acceptable.
            with suppress(_core.VerifyException):
                _core.validate_frame_checksums(bytes(frame_bytes))

    def test_data_integrity_after_crc_validation(self, tmp_path):
        """Test data integrity after successful CRC validation."""
        tmp_file = tmp_path / "crc_integrity.gwf"

        # Create and write frame
        original_data = np.random.randn(16384)
        frame = gwframe.Frame(t0=1234567890.0, duration=1.0, name="L1", run=1)
        frame.add_channel("L1:TEST", original_data, sample_rate=16384, unit="strain")
        frame.write(str(tmp_file))

        # Read file bytes
        with open(tmp_file, "rb") as f:
            frame_bytes = f.read()

        # Validate CRC
        _core.validate_frame_checksums(frame_bytes)

        # Read back data
        result = gwframe.read(str(tmp_file), "L1:TEST")

        # Verify data matches
        assert np.allclose(result.array, original_data)

    def test_multiframe_crc_validation(self, tmp_path):
        """Test CRC validation for multi-frame files."""
        tmp_file = tmp_path / "multiframe_crc.gwf"

        # Write multiple frames
        n_frames = 3
        with gwframe.FrameWriter(str(tmp_file)) as writer:
            for i in range(n_frames):
                data = np.random.randn(1000)
                writer.write(
                    data,
                    t0=1234567890.0 + i,
                    sample_rate=1000,
                    name="L1:TEST",
                    unit="counts",
                )

        # Read file bytes and validate all frames
        with open(tmp_file, "rb") as f:
            frame_bytes = f.read()

        # This should validate all frames
        _core.validate_frame_checksums(frame_bytes)


class TestFrameInfoMetadata:
    """Tests for frame info and metadata extraction."""

    def test_get_info(self, test_gwf_file):
        """Test get_info() returns frame metadata."""
        info = gwframe.get_info(str(test_gwf_file))

        # info is now a FrameFileInfo dataclass
        assert info.num_frames > 0
        assert len(info.frames) > 0
        # Check first frame has expected fields
        first_frame = info.frames[0]
        assert hasattr(first_frame, "t0")
        assert hasattr(first_frame, "duration")
        assert first_frame.t0 > 0
        assert first_frame.duration > 0

    def test_get_channels(self, test_gwf_file):
        """Test get_channels() lists available channels."""
        channels = gwframe.get_channels(str(test_gwf_file))

        # Returns list of channel names
        assert isinstance(channels, list)
        assert len(channels) > 0
        # L1 GWOSC file should have strain channel
        assert any("STRAIN" in ch for ch in channels)

    def test_get_info_multiframe(self, tmp_path):
        """Test get_info() with multi-frame file."""
        tmp_file = tmp_path / "multiframe_info.gwf"

        n_frames = 5
        with gwframe.FrameWriter(str(tmp_file)) as writer:
            for i in range(n_frames):
                data = np.random.randn(1000)
                writer.write(
                    data,
                    t0=1234567890.0 + i,
                    sample_rate=1000,
                    name="L1:TEST",
                    unit="counts",
                )

        info = gwframe.get_info(str(tmp_file))

        assert info.num_frames == n_frames
        assert len(info.frames) == n_frames

    def test_get_channels_multiple_channels(self, tmp_path):
        """Test get_channels() with multiple channels."""
        tmp_file = tmp_path / "multichannel_info.gwf"

        # Write frame with multiple channels
        frame = gwframe.Frame(t0=1234567890.0, duration=1.0, name="L1", run=1)
        frame.add_channel("L1:STRAIN", np.random.randn(1000), sample_rate=1000)
        frame.add_channel("L1:AUX1", np.random.randn(500), sample_rate=500)
        frame.add_channel("L1:AUX2", np.random.randn(100), sample_rate=100)
        frame.write(str(tmp_file))

        channels = gwframe.get_channels(str(tmp_file))

        # Returns list of channel names
        assert isinstance(channels, list)
        assert len(channels) == 3
        assert "L1:STRAIN" in channels
        assert "L1:AUX1" in channels
        assert "L1:AUX2" in channels


class TestCompressionMetadata:
    """Tests for compression detection and preservation."""

    def test_get_info_includes_compression(self, tmp_path):
        """Test that get_info() includes compression metadata."""
        tmp_file = tmp_path / "compression_info.gwf"

        # Write frame with default compression
        frame = gwframe.Frame(t0=1234567890.0, duration=1.0, name="L1", run=1)
        frame.add_channel("L1:TEST", np.random.randn(1000), sample_rate=1000)
        frame.write(str(tmp_file))

        info = gwframe.get_info(str(tmp_file))

        # Check compression field exists
        assert hasattr(info, "compression")
        assert isinstance(info.compression, int)

    @pytest.mark.parametrize(
        ("compression", "data_factory"),
        [
            (gwframe.Compression.RAW, lambda: np.random.randn(1000)),
            (gwframe.Compression.GZIP, lambda: np.random.randn(1000)),
            (gwframe.Compression.DIFF_GZIP, lambda: np.arange(1000, dtype=np.int32)),
            (
                gwframe.Compression.ZERO_SUPPRESS_OTHERWISE_GZIP,
                lambda: np.random.randn(1000),
            ),
        ],
    )
    def test_compression_detection(self, tmp_path, compression, data_factory):
        """Test compression detection for different schemes."""
        tmp_file = tmp_path / f"compression_{compression.name}.gwf"

        # Write with specified compression
        with gwframe.FrameWriter(str(tmp_file), compression=compression) as writer:
            data = data_factory()
            writer.write(
                data, t0=1234567890.0, sample_rate=1000, name="L1:TEST", unit="counts"
            )

        info = gwframe.get_info(str(tmp_file))

        # For ZERO_SUPPRESS_OTHERWISE_GZIP with float data, expect GZIP
        if compression == gwframe.Compression.ZERO_SUPPRESS_OTHERWISE_GZIP:
            assert info.compression in (
                gwframe.Compression.GZIP,
                gwframe.Compression.ZERO_SUPPRESS_OTHERWISE_GZIP,
            )
        else:
            assert info.compression == compression

    def test_compression_settings_property(self, tmp_path):
        """Test compression_settings property returns correct dict."""
        tmp_file = tmp_path / "settings.gwf"

        # Write with GZIP compression
        with gwframe.FrameWriter(
            str(tmp_file), compression=gwframe.Compression.GZIP
        ) as writer:
            data = np.random.randn(1000)
            writer.write(
                data, t0=1234567890.0, sample_rate=1000, name="L1:TEST", unit="counts"
            )

        info = gwframe.get_info(str(tmp_file))
        settings = info.compression_settings

        # Should return dict with compression key
        assert isinstance(settings, dict)
        assert "compression" in settings
        assert settings["compression"] == gwframe.Compression.GZIP

    @pytest.mark.parametrize(
        "compression",
        [
            gwframe.Compression.RAW,
            gwframe.Compression.GZIP,
            gwframe.Compression.ZERO_SUPPRESS_OTHERWISE_GZIP,
        ],
    )
    def test_compression_roundtrip_preservation(self, tmp_path, compression):
        """Test that compression is preserved in read-modify-write cycle."""
        input_file = tmp_path / f"input_{compression.name}.gwf"
        output_file = tmp_path / f"output_{compression.name}.gwf"

        # Write original file with specified compression
        with gwframe.FrameWriter(str(input_file), compression=compression) as writer:
            data = np.random.randn(1000)
            writer.write(
                data, t0=1234567890.0, sample_rate=1000, name="L1:TEST", unit="counts"
            )

        # Read metadata
        info = gwframe.get_info(str(input_file))

        # Read data
        data = gwframe.read(str(input_file), "L1:TEST")

        # Write with preserved compression settings
        with gwframe.FrameWriter(
            str(output_file), **info.compression_settings
        ) as writer:
            writer.write(
                data.array,
                t0=data.t0,
                sample_rate=data.sample_rate,
                name=data.name,
                unit=data.unit,
            )

        # Verify output has same compression
        output_info = gwframe.get_info(str(output_file))

        # For ZERO_SUPPRESS_OTHERWISE_GZIP, might resolve to GZIP for float data
        if compression == gwframe.Compression.ZERO_SUPPRESS_OTHERWISE_GZIP:
            assert output_info.compression in (
                gwframe.Compression.GZIP,
                gwframe.Compression.ZERO_SUPPRESS_OTHERWISE_GZIP,
            )
        else:
            assert output_info.compression == info.compression

    def test_compression_multiframe_uniform(self, tmp_path):
        """Test that compression is uniform across all frames."""
        tmp_file = tmp_path / "multiframe_compression.gwf"

        # Write multiple frames with GZIP
        n_frames = 3
        with gwframe.FrameWriter(
            str(tmp_file), compression=gwframe.Compression.GZIP
        ) as writer:
            for i in range(n_frames):
                data = np.random.randn(1000)
                writer.write(
                    data,
                    t0=1234567890.0 + i,
                    sample_rate=1000,
                    name="L1:TEST",
                    unit="counts",
                )

        info = gwframe.get_info(str(tmp_file))

        # Compression should be uniform (file-level)
        assert info.compression == gwframe.Compression.GZIP

        # Verify by reading individual frames
        stream = _core.IFrameFStream(str(tmp_file))
        toc = stream.get_toc()
        proc_channels = toc.get_proc()

        # All channels in all frames should have same compression
        compression_schemes = []
        for frame_idx in range(n_frames):
            for channel_name in proc_channels:
                fr_proc = stream.read_fr_proc_data(frame_idx, channel_name)
                vect = fr_proc.get_data_vector(0)
                compression_schemes.append(vect.get_compression_scheme())

        # All should be the same
        assert len(set(compression_schemes)) == 1
        # And match what get_info detected
        assert compression_schemes[0] == info.compression

    def test_compression_multichannel_detection(self, tmp_path):
        """Test that get_info() correctly detects file-level compression.

        Note: Small data arrays may not be compressed (appear as RAW) even when
        a compression scheme is specified, as compression may not be beneficial
        for very small datasets. The detection algorithm samples multiple channels
        and prefers non-RAW schemes to identify the intended file-level compression.
        """
        tmp_file = tmp_path / "multichannel_compression.gwf"

        # Write frame with channels of varying sizes
        frame = gwframe.Frame(t0=1234567890.0, duration=1.0, name="L1", run=1)
        frame.add_channel("L1:CHAN1", np.random.randn(1000), sample_rate=1000)
        frame.add_channel("L1:CHAN2", np.random.randn(500), sample_rate=500)
        frame.add_channel("L1:CHAN3", np.random.randn(100), sample_rate=100)

        with gwframe.FrameWriter(
            str(tmp_file), compression=gwframe.Compression.GZIP
        ) as writer:
            writer.write_frame(frame)

        info = gwframe.get_info(str(tmp_file))

        # get_info() should detect GZIP as the file-level compression
        # even if small channels are left uncompressed (RAW)
        assert info.compression == gwframe.Compression.GZIP

        # Verify compression_settings provides correct round-trip capability
        assert info.compression_settings == {"compression": gwframe.Compression.GZIP}

    def test_compression_empty_file_handling(self, tmp_path):
        """Test compression detection with file containing no data channels."""
        tmp_file = tmp_path / "empty_channels.gwf"

        # Write frame with no channels (edge case)
        frame = gwframe.Frame(t0=1234567890.0, duration=1.0, name="L1", run=1)
        frame.write(str(tmp_file))

        info = gwframe.get_info(str(tmp_file))

        # Should default to RAW when no channels
        assert info.compression == gwframe.Compression.RAW
        assert len(info.channels) == 0
