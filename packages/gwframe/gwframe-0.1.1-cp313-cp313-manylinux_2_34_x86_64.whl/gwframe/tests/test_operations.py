"""Comprehensive tests for gwframe operations module."""

from pathlib import Path

import numpy as np
import pytest

import gwframe
from gwframe import operations
from gwframe.write import Frame, FrameWriter


@pytest.fixture
def sample_data():
    """Generate sample data for testing."""
    return {
        "t0": 1234567890.0,
        "duration": 1.0,
        "sample_rate": 16.0,
        "n_samples": 16,
    }


@pytest.fixture
def create_test_frame():
    """Factory fixture to create test frames with specified channels."""

    def _create_frame(t0, duration, channels, frame_number=0):
        """
        Create a frame with specified channels.

        Parameters
        ----------
        t0 : float
            Frame start time
        duration : float
            Frame duration
        channels : dict
            Dictionary mapping channel names to data arrays
        frame_number : int
            Frame number

        Returns
        -------
        frame : Frame
            Created frame object
        """
        frame = Frame(
            t0=t0, duration=duration, name="TEST", run=1, frame_number=frame_number
        )
        for channel_name, data in channels.items():
            sample_rate = len(data) / duration
            frame.add_channel(
                channel_name, data, sample_rate=sample_rate, unit="counts"
            )
        return frame

    return _create_frame


@pytest.fixture
def single_frame_file(tmp_path, sample_data, create_test_frame):
    """Create a single-frame GWF file for testing."""
    file_path = tmp_path / "single.gwf"
    n_samples = sample_data["n_samples"]

    with FrameWriter(str(file_path)) as writer:
        channels = {
            "L1:CHAN1": np.arange(n_samples, dtype=np.float32),
            "L1:CHAN2": np.arange(n_samples, dtype=np.float32) * 2,
            "L1:CHAN3": np.arange(n_samples, dtype=np.float32) * 3,
        }
        frame = create_test_frame(
            sample_data["t0"], sample_data["duration"], channels, frame_number=0
        )
        writer.write_frame(frame)

    return file_path


@pytest.fixture
def multi_frame_file(tmp_path, sample_data, create_test_frame):
    """Create a multi-frame GWF file for testing."""
    file_path = tmp_path / "multi.gwf"
    n_frames = 3
    n_samples = sample_data["n_samples"]

    with FrameWriter(str(file_path)) as writer:
        for i in range(n_frames):
            t0 = sample_data["t0"] + i * sample_data["duration"]
            channels = {
                "L1:DATA": np.full(n_samples, float(i), dtype=np.float32),
                "L1:AUX": np.full(n_samples, float(i * 10), dtype=np.float32),
            }
            frame = create_test_frame(
                t0, sample_data["duration"], channels, frame_number=i
            )
            writer.write_frame(frame)

    return file_path


@pytest.fixture
def multiple_files(tmp_path, sample_data, create_test_frame):
    """Create multiple GWF files for testing operations that work on file sets."""
    files = []
    n_files = 3
    n_samples = sample_data["n_samples"]

    for file_idx in range(n_files):
        file_path = tmp_path / f"file{file_idx + 1}.gwf"
        files.append(file_path)

        with FrameWriter(str(file_path)) as writer:
            for frame_idx in range(2):  # 2 frames per file
                global_idx = file_idx * 2 + frame_idx
                t0 = sample_data["t0"] + global_idx * sample_data["duration"]
                channels = {
                    "L1:DATA": np.arange(n_samples, dtype=np.float32)
                    + global_idx * n_samples,
                }
                frame = create_test_frame(
                    t0, sample_data["duration"], channels, frame_number=global_idx
                )
                writer.write_frame(frame)

    return files


class TestRenameChannels:
    """Tests for rename_channels operation."""

    def test_rename_single_file(self, single_frame_file, tmp_path):
        """Test renaming channels in a single file."""
        output_dir = tmp_path / "output"
        channel_map = {"L1:CHAN1": "L1:NEW_CHAN1", "L1:CHAN2": "L1:NEW_CHAN2"}

        output_files = operations.rename_channels(
            str(single_frame_file), str(output_dir), channel_map
        )

        assert len(output_files) == 1
        assert Path(output_files[0]).exists()

        # Verify renamed channels
        frames = list(gwframe.read_frames(output_files[0]))
        assert "L1:NEW_CHAN1" in frames[0]
        assert "L1:NEW_CHAN2" in frames[0]
        assert "L1:CHAN3" in frames[0]  # Unchanged
        assert "L1:CHAN1" not in frames[0]
        assert "L1:CHAN2" not in frames[0]

    @pytest.mark.parametrize(
        "input_type",
        ["single_file", "list_of_files"],
    )
    def test_rename_input_types(self, multiple_files, tmp_path, input_type):
        """Test rename with different input types."""
        output_dir = tmp_path / "output"
        channel_map = {"L1:DATA": "L1:RENAMED_DATA"}

        if input_type == "single_file":
            input_files = str(multiple_files[0])
            expected_count = 1
        else:  # list_of_files
            input_files = [str(f) for f in multiple_files]
            expected_count = len(multiple_files)

        output_files = operations.rename_channels(
            input_files, str(output_dir), channel_map
        )

        assert len(output_files) == expected_count
        for output_file in output_files:
            frames = list(gwframe.read_frames(output_file))
            assert "L1:RENAMED_DATA" in frames[0]
            assert "L1:DATA" not in frames[0]


class TestDropChannels:
    """Tests for drop_channels operation."""

    def test_drop_single_channel(self, single_frame_file, tmp_path):
        """Test dropping a single channel."""
        output_dir = tmp_path / "output"
        channels_to_drop = ["L1:CHAN2"]

        output_files = operations.drop_channels(
            str(single_frame_file), str(output_dir), channels_to_drop
        )

        assert len(output_files) == 1

        # Verify channel was dropped
        frames = list(gwframe.read_frames(output_files[0]))
        assert "L1:CHAN1" in frames[0]
        assert "L1:CHAN3" in frames[0]
        assert "L1:CHAN2" not in frames[0]

    @pytest.mark.parametrize(
        ("channels_to_drop", "expected_remaining"),
        [
            (["L1:CHAN1"], ["L1:CHAN2", "L1:CHAN3"]),
            (["L1:CHAN1", "L1:CHAN2"], ["L1:CHAN3"]),
            (["L1:CHAN1", "L1:CHAN2", "L1:CHAN3"], []),
        ],
    )
    def test_drop_multiple_channels(
        self, single_frame_file, tmp_path, channels_to_drop, expected_remaining
    ):
        """Test dropping different numbers of channels."""
        output_dir = tmp_path / "output"

        output_files = operations.drop_channels(
            str(single_frame_file), str(output_dir), channels_to_drop
        )

        frames = list(gwframe.read_frames(output_files[0]))
        remaining_channels = list(frames[0].keys())

        assert set(remaining_channels) == set(expected_remaining)


class TestResizeFrames:
    """Tests for resize_frames operation."""

    def test_resize_split_frames(self, multi_frame_file, tmp_path, sample_data):
        """Test splitting frames into smaller duration."""
        output_dir = tmp_path / "output"
        target_duration = sample_data["duration"] / 2  # Split each frame in half

        output_files = operations.resize_frames(
            str(multi_frame_file), str(output_dir), target_duration
        )

        assert len(output_files) == 1

        # Should have double the frames
        frames = list(gwframe.read_frames(output_files[0]))
        assert len(frames) == 6  # 3 original frames x 2

        # Verify durations
        for frame in frames:
            assert abs(frame.duration - target_duration) < 1e-9

    def test_resize_preserve_data(self, multi_frame_file, tmp_path, sample_data):
        """Test that resizing preserves data values."""
        output_dir = tmp_path / "output"
        target_duration = sample_data["duration"] / 2

        output_files = operations.resize_frames(
            str(multi_frame_file), str(output_dir), target_duration
        )

        frames = list(gwframe.read_frames(output_files[0]))

        # First original frame had value 0.0
        assert np.allclose(frames[0]["L1:DATA"].array, 0.0)
        assert np.allclose(frames[1]["L1:DATA"].array, 0.0)

        # Second original frame had value 1.0
        assert np.allclose(frames[2]["L1:DATA"].array, 1.0)
        assert np.allclose(frames[3]["L1:DATA"].array, 1.0)

    def test_resize_no_split(self, multi_frame_file, tmp_path, sample_data):
        """Test that frames are kept when target duration >= source duration."""
        output_dir = tmp_path / "output"
        target_duration = sample_data["duration"] * 2  # Double the source duration

        output_files = operations.resize_frames(
            str(multi_frame_file), str(output_dir), target_duration
        )

        frames = list(gwframe.read_frames(output_files[0]))

        # Should have same number of frames as original (no splitting/merging)
        assert len(frames) == 3

        # Frames should keep their original duration
        for frame in frames:
            assert abs(frame.duration - sample_data["duration"]) < 1e-9

        # Data should be preserved
        assert np.allclose(frames[0]["L1:DATA"].array, 0.0)
        assert np.allclose(frames[1]["L1:DATA"].array, 1.0)
        assert np.allclose(frames[2]["L1:DATA"].array, 2.0)


class TestImputeMissingData:
    """Tests for impute_missing_data operation."""

    def test_impute_nan_values(self, tmp_path, sample_data, create_test_frame):
        """Test imputing NaN values with zeros."""
        # Create file with NaN values
        file_path = tmp_path / "with_nan.gwf"
        data = np.array([1.0, 2.0, np.nan, 4.0, np.nan, 6.0], dtype=np.float32)

        with FrameWriter(str(file_path)) as writer:
            channels = {"L1:DATA": data}
            frame = create_test_frame(
                sample_data["t0"], sample_data["duration"], channels
            )
            writer.write_frame(frame)

        output_dir = tmp_path / "output"

        output_files = operations.impute_missing_data(
            str(file_path),
            str(output_dir),
            replace_value=np.nan,
            fill_value=0.0,
        )

        # Verify NaN values were replaced
        frames = list(gwframe.read_frames(output_files[0]))
        result_data = frames[0]["L1:DATA"].array

        expected = np.array([1.0, 2.0, 0.0, 4.0, 0.0, 6.0], dtype=np.float32)
        assert np.allclose(result_data, expected)

    @pytest.mark.parametrize(
        ("replace_value", "fill_value", "input_data", "expected_data"),
        [
            (np.nan, 0.0, [1.0, np.nan, 3.0], [1.0, 0.0, 3.0]),
            (-999.0, 0.0, [1.0, -999.0, 3.0], [1.0, 0.0, 3.0]),
            (0.0, 100.0, [1.0, 0.0, 3.0], [1.0, 100.0, 3.0]),
        ],
    )
    def test_impute_different_values(
        self,
        tmp_path,
        sample_data,
        create_test_frame,
        replace_value,
        fill_value,
        input_data,
        expected_data,
    ):
        """Test imputing different replacement and fill values."""
        file_path = tmp_path / "test.gwf"
        data = np.array(input_data, dtype=np.float32)

        with FrameWriter(str(file_path)) as writer:
            channels = {"L1:DATA": data}
            frame = create_test_frame(
                sample_data["t0"], sample_data["duration"], channels
            )
            writer.write_frame(frame)

        output_dir = tmp_path / "output"

        output_files = operations.impute_missing_data(
            str(file_path),
            str(output_dir),
            replace_value=replace_value,
            fill_value=fill_value,
        )

        frames = list(gwframe.read_frames(output_files[0]))
        result_data = frames[0]["L1:DATA"].array

        expected = np.array(expected_data, dtype=np.float32)
        # Use nanclose for NaN comparisons
        if np.isnan(replace_value):
            assert np.allclose(result_data, expected, equal_nan=True)
        else:
            assert np.allclose(result_data, expected)


class TestReplaceChannels:
    """Tests for replace_channels operation."""

    def test_replace_channel_data(self, tmp_path, sample_data, create_test_frame):
        """Test replacing channel data from another file."""
        # Create base file
        base_file = tmp_path / "base.gwf"
        base_data = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)

        with FrameWriter(str(base_file)) as writer:
            channels = {"L1:DATA": base_data, "L1:AUX": base_data * 2}
            frame = create_test_frame(
                sample_data["t0"], sample_data["duration"], channels
            )
            writer.write_frame(frame)

        # Create update file with new data
        update_file = tmp_path / "update.gwf"
        update_data = np.array([10.0, 20.0, 30.0, 40.0], dtype=np.float32)

        with FrameWriter(str(update_file)) as writer:
            channels = {"L1:DATA": update_data}
            frame = create_test_frame(
                sample_data["t0"], sample_data["duration"], channels
            )
            writer.write_frame(frame)

        output_dir = tmp_path / "output"

        output_files = operations.replace_channels(
            str(base_file),
            str(update_file),
            str(output_dir),
            channels_to_replace=["L1:DATA"],
        )

        # Verify L1:DATA was updated, L1:AUX unchanged
        frames = list(gwframe.read_frames(output_files[0]))
        assert np.allclose(frames[0]["L1:DATA"].array, update_data)
        assert np.allclose(frames[0]["L1:AUX"].array, base_data * 2)


class TestRecompressFrames:
    """Tests for recompress_frames operation."""

    @pytest.mark.parametrize(
        ("compression", "level"),
        [
            (gwframe.Compression.RAW, 0),
            (gwframe.Compression.GZIP, 1),
            (gwframe.Compression.GZIP, 9),
        ],
    )
    def test_recompress_different_settings(
        self, single_frame_file, tmp_path, compression, level
    ):
        """Test recompressing with different compression settings."""
        output_dir = tmp_path / "output"

        output_files = operations.recompress_frames(
            str(single_frame_file), str(output_dir), compression, level
        )

        assert len(output_files) == 1
        assert Path(output_files[0]).exists()

        # Verify data integrity after recompression
        frames = list(gwframe.read_frames(output_files[0]))
        assert "L1:CHAN1" in frames[0]
        assert "L1:CHAN2" in frames[0]
        assert "L1:CHAN3" in frames[0]


class TestCombineChannels:
    """Tests for combine_channels operation."""

    def test_combine_two_files(self, tmp_path, sample_data, create_test_frame):
        """Test combining channels from two files."""
        # Create two files with different channels covering same time
        file1 = tmp_path / "file1.gwf"
        file2 = tmp_path / "file2.gwf"
        n_samples = sample_data["n_samples"]

        data1 = np.arange(n_samples, dtype=np.float32)
        data2 = np.arange(n_samples, dtype=np.float32) * 2

        with FrameWriter(str(file1)) as writer:
            channels = {"L1:CHAN_A": data1}
            frame = create_test_frame(
                sample_data["t0"], sample_data["duration"], channels
            )
            writer.write_frame(frame)

        with FrameWriter(str(file2)) as writer:
            channels = {"L1:CHAN_B": data2}
            frame = create_test_frame(
                sample_data["t0"], sample_data["duration"], channels
            )
            writer.write_frame(frame)

        output_dir = tmp_path / "output"

        output_files = operations.combine_channels(
            [str(file1), str(file2)], str(output_dir)
        )

        assert len(output_files) == 1

        # Verify both channels are present
        frames = list(gwframe.read_frames(output_files[0]))
        assert "L1:CHAN_A" in frames[0]
        assert "L1:CHAN_B" in frames[0]
        assert np.allclose(frames[0]["L1:CHAN_A"].array, data1)
        assert np.allclose(frames[0]["L1:CHAN_B"].array, data2)

    def test_combine_with_keep_channels(self, tmp_path, sample_data, create_test_frame):
        """Test combining with channel filtering (keep)."""
        file1 = tmp_path / "file1.gwf"
        file2 = tmp_path / "file2.gwf"
        n_samples = sample_data["n_samples"]

        data = np.arange(n_samples, dtype=np.float32)

        with FrameWriter(str(file1)) as writer:
            channels = {"L1:CHAN_A": data, "L1:CHAN_B": data * 2}
            frame = create_test_frame(
                sample_data["t0"], sample_data["duration"], channels
            )
            writer.write_frame(frame)

        with FrameWriter(str(file2)) as writer:
            channels = {"L1:CHAN_C": data * 3}
            frame = create_test_frame(
                sample_data["t0"], sample_data["duration"], channels
            )
            writer.write_frame(frame)

        output_dir = tmp_path / "output"

        output_files = operations.combine_channels(
            [str(file1), str(file2)],
            str(output_dir),
            keep_channels=["L1:CHAN_A", "L1:CHAN_C"],
        )

        frames = list(gwframe.read_frames(output_files[0]))
        assert "L1:CHAN_A" in frames[0]
        assert "L1:CHAN_C" in frames[0]
        assert "L1:CHAN_B" not in frames[0]  # Filtered out

    def test_combine_directories(self, tmp_path, sample_data, create_test_frame):
        """Test combining channels from multiple directories with matching frames."""
        # Create two directories with matching time ranges
        dir1 = tmp_path / "dir1"
        dir2 = tmp_path / "dir2"
        dir1.mkdir()
        dir2.mkdir()

        n_samples = sample_data["n_samples"]
        n_files = 3

        # Create matching frame sets in both directories
        for i in range(n_files):
            t0 = sample_data["t0"] + i * sample_data["duration"]

            # Directory 1: CHAN_A
            file1 = dir1 / f"frame_{i}.gwf"
            data_a = np.full(n_samples, float(i), dtype=np.float32)
            with FrameWriter(str(file1)) as writer:
                channels = {"L1:CHAN_A": data_a}
                frame = create_test_frame(t0, sample_data["duration"], channels)
                writer.write_frame(frame)

            # Directory 2: CHAN_B
            file2 = dir2 / f"frame_{i}.gwf"
            data_b = np.full(n_samples, float(i * 10), dtype=np.float32)
            with FrameWriter(str(file2)) as writer:
                channels = {"L1:CHAN_B": data_b}
                frame = create_test_frame(t0, sample_data["duration"], channels)
                writer.write_frame(frame)

        output_dir = tmp_path / "output"

        output_files = operations.combine_channels(
            [str(dir1), str(dir2)], str(output_dir)
        )

        # Should create one combined file per time range
        assert len(output_files) == n_files

        # Verify each output file has both channels
        for i, output_file in enumerate(sorted(output_files)):
            frames = list(gwframe.read_frames(output_file))
            assert len(frames) == 1

            # Both channels should be present
            assert "L1:CHAN_A" in frames[0]
            assert "L1:CHAN_B" in frames[0]

            # Verify data values
            assert np.allclose(frames[0]["L1:CHAN_A"].array, float(i))
            assert np.allclose(frames[0]["L1:CHAN_B"].array, float(i * 10))
