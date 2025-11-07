"""Tests for gwframe CLI commands."""

from __future__ import annotations

import shutil

import numpy as np
import pytest
from typer.testing import CliRunner

import gwframe
from gwframe.cli import app

# Import fixtures from test_operations
pytest_plugins = ["gwframe.tests.test_operations"]

runner = CliRunner()


class TestRenameCommand:
    """Tests for gwframe rename command."""

    def test_rename_basic(self, single_frame_file, tmp_path):
        """Test basic rename command."""
        output_dir = tmp_path / "output"

        result = runner.invoke(
            app,
            [
                "rename",
                str(single_frame_file),
                "-o",
                str(output_dir),
                "-m",
                "L1:CHAN1=>L1:RENAMED1",
                "-m",
                "L1:CHAN2=>L1:RENAMED2",
            ],
        )

        assert result.exit_code == 0, result.stdout
        assert output_dir.exists()

        # Verify channels were renamed
        output_file = output_dir / single_frame_file.name
        channels = gwframe.get_channels(str(output_file))
        assert "L1:RENAMED1" in channels
        assert "L1:RENAMED2" in channels
        assert "L1:CHAN1" not in channels
        assert "L1:CHAN2" not in channels

    def test_rename_in_place(self, single_frame_file, tmp_path):
        """Test rename with --in-place."""
        # Copy file to tmp_path so we can modify it
        test_file = tmp_path / "test.gwf"
        shutil.copy(single_frame_file, test_file)

        result = runner.invoke(
            app,
            [
                "rename",
                str(test_file),
                "-i",
                "-m",
                "L1:CHAN1=>L1:RENAMED",
            ],
        )

        assert result.exit_code == 0, result.stdout

        # Verify file was modified in place
        channels = gwframe.get_channels(str(test_file))
        assert "L1:RENAMED" in channels
        assert "L1:CHAN1" not in channels

    def test_rename_single_file_output(self, single_frame_file, tmp_path):
        """Test rename with single file output."""
        output_file = tmp_path / "output.gwf"

        result = runner.invoke(
            app,
            [
                "rename",
                str(single_frame_file),
                "-o",
                str(output_file),
                "-m",
                "L1:CHAN1=>L1:RENAMED",
            ],
        )

        assert result.exit_code == 0, result.stdout
        assert output_file.exists()

        # Verify channels were renamed
        channels = gwframe.get_channels(str(output_file))
        assert "L1:RENAMED" in channels

    def test_rename_mutual_exclusivity(self, single_frame_file, tmp_path):
        """Test that --in-place and -o are mutually exclusive."""
        output_dir = tmp_path / "output"

        result = runner.invoke(
            app,
            [
                "rename",
                str(single_frame_file),
                "-o",
                str(output_dir),
                "-i",
                "-m",
                "L1:CHAN1=>TEST:RENAMED",
            ],
        )

        assert result.exit_code != 0
        assert "mutually exclusive" in result.stdout.lower()


class TestDropCommand:
    """Tests for gwframe drop command."""

    def test_drop_basic(self, single_frame_file, tmp_path):
        """Test basic drop command."""
        output_dir = tmp_path / "output"

        result = runner.invoke(
            app,
            [
                "drop",
                str(single_frame_file),
                "-o",
                str(output_dir),
                "-c",
                "L1:CHAN1",
            ],
        )

        assert result.exit_code == 0, result.stdout

        # Verify channel was dropped
        output_file = output_dir / single_frame_file.name
        channels = gwframe.get_channels(str(output_file))
        assert "L1:CHAN1" not in channels
        assert "L1:CHAN2" in channels

    def test_drop_in_place(self, single_frame_file, tmp_path):
        """Test drop with --in-place."""
        test_file = tmp_path / "test.gwf"
        shutil.copy(single_frame_file, test_file)

        result = runner.invoke(app, ["drop", str(test_file), "-i", "-c", "L1:CHAN1"])

        assert result.exit_code == 0, result.stdout

        # Verify channel was dropped
        channels = gwframe.get_channels(str(test_file))
        assert "L1:CHAN1" not in channels
        assert "L1:CHAN2" in channels

    def test_drop_multiple_channels(self, single_frame_file, tmp_path):
        """Test dropping multiple channels."""
        output_dir = tmp_path / "output"

        result = runner.invoke(
            app,
            [
                "drop",
                str(single_frame_file),
                "-o",
                str(output_dir),
                "-c",
                "L1:CHAN1",
                "-c",
                "L1:CHAN2",
            ],
        )

        assert result.exit_code == 0, result.stdout

        # Verify both channels were dropped
        output_file = output_dir / single_frame_file.name
        channels = gwframe.get_channels(str(output_file))
        assert "L1:CHAN1" not in channels
        assert "L1:CHAN2" not in channels


class TestResizeCommand:
    """Tests for gwframe resize command."""

    def test_resize_basic(self, multi_frame_file, tmp_path, sample_data):
        """Test basic resize command."""
        output_dir = tmp_path / "output"
        target_duration = sample_data["duration"] / 2

        result = runner.invoke(
            app,
            [
                "resize",
                str(multi_frame_file),
                "-o",
                str(output_dir),
                "-d",
                str(target_duration),
            ],
        )

        assert result.exit_code == 0, result.stdout

        # Verify frames were resized
        output_file = output_dir / multi_frame_file.name
        frames = list(gwframe.read_frames(str(output_file)))
        # Each of 3 original frames split in 2 = 6 frames
        assert len(frames) == 6
        for frame in frames:
            assert abs(frame.duration - target_duration) < 1e-9

    def test_resize_in_place(self, multi_frame_file, tmp_path, sample_data):
        """Test resize with --in-place."""
        test_file = tmp_path / "test.gwf"
        shutil.copy(multi_frame_file, test_file)
        target_duration = sample_data["duration"] / 2

        result = runner.invoke(
            app, ["resize", str(test_file), "-i", "-d", str(target_duration)]
        )

        assert result.exit_code == 0, result.stdout

        # Verify frames were resized in place
        frames = list(gwframe.read_frames(str(test_file)))
        assert len(frames) == 6


class TestImputeCommand:
    """Tests for gwframe impute command."""

    def test_impute_basic(self, tmp_path):
        """Test basic impute command."""
        # Create a file with NaN values
        input_file = tmp_path / "input.gwf"
        data_with_nan = np.array([1.0, 2.0, np.nan, 4.0, np.nan])

        gwframe.write(
            str(input_file),
            data_with_nan,
            t0=1234567890.0,
            sample_rate=1,
            name="L1:CHAN",
        )

        output_dir = tmp_path / "output"

        result = runner.invoke(
            app, ["impute", str(input_file), "-o", str(output_dir), "-f", "0.0"]
        )

        assert result.exit_code == 0, result.stdout

        # Verify NaNs were replaced
        output_file = output_dir / input_file.name
        data = gwframe.read(str(output_file), "L1:CHAN")
        assert not np.any(np.isnan(data.array))
        assert data.array[2] == 0.0
        assert data.array[4] == 0.0

    def test_impute_in_place(self, tmp_path):
        """Test impute with --in-place."""
        test_file = tmp_path / "test.gwf"
        data_with_nan = np.array([1.0, np.nan, 3.0])

        gwframe.write(
            str(test_file),
            data_with_nan,
            t0=1234567890.0,
            sample_rate=1,
            name="L1:CHAN",
        )

        result = runner.invoke(app, ["impute", str(test_file), "-i", "-f", "999.0"])

        assert result.exit_code == 0, result.stdout

        # Verify NaNs were replaced in place
        data = gwframe.read(str(test_file), "L1:CHAN")
        assert data.array[1] == 999.0

    def test_impute_specific_value(self, tmp_path):
        """Test impute replacing specific value."""
        input_file = tmp_path / "input.gwf"
        data = np.array([1.0, -999.0, 3.0, -999.0])

        gwframe.write(
            str(input_file),
            data,
            t0=1234567890.0,
            sample_rate=1,
            name="L1:CHAN",
        )

        output_dir = tmp_path / "output"

        result = runner.invoke(
            app,
            [
                "impute",
                str(input_file),
                "-o",
                str(output_dir),
                "-r",
                "-999.0",
                "-f",
                "0.0",
            ],
        )

        assert result.exit_code == 0, result.stdout

        # Verify -999.0 values were replaced
        output_file = output_dir / input_file.name
        result_data = gwframe.read(str(output_file), "L1:CHAN")
        assert result_data.array[1] == 0.0
        assert result_data.array[3] == 0.0


class TestCombineCommand:
    """Tests for gwframe combine command."""

    def test_combine_files_with_filtering(
        self, tmp_path, sample_data, create_test_frame
    ):
        """Test combine command with files and channel filtering."""
        # Create two files with different channels
        file1 = tmp_path / "file1.gwf"
        file2 = tmp_path / "file2.gwf"
        n_samples = sample_data["n_samples"]

        data = np.arange(n_samples, dtype=np.float32)

        with gwframe.FrameWriter(str(file1)) as writer:
            channels = {"L1:CHAN_A": data, "L1:CHAN_B": data * 2}
            frame = create_test_frame(
                sample_data["t0"], sample_data["duration"], channels
            )
            writer.write_frame(frame)

        with gwframe.FrameWriter(str(file2)) as writer:
            channels = {"L1:CHAN_C": data * 3}
            frame = create_test_frame(
                sample_data["t0"], sample_data["duration"], channels
            )
            writer.write_frame(frame)

        output_dir = tmp_path / "output"

        # Test basic combine
        result = runner.invoke(
            app, ["combine", str(file1), str(file2), "-o", str(output_dir)]
        )
        assert result.exit_code == 0, result.stdout

        output_files = list(output_dir.glob("*.gwf"))
        frames = list(gwframe.read_frames(str(output_files[0])))
        assert "L1:CHAN_A" in frames[0]
        assert "L1:CHAN_B" in frames[0]
        assert "L1:CHAN_C" in frames[0]

        # Test with --keep filtering
        output_dir_keep = tmp_path / "output_keep"
        result = runner.invoke(
            app,
            [
                "combine",
                str(file1),
                str(file2),
                "-o",
                str(output_dir_keep),
                "-k",
                "L1:CHAN_A",
                "-k",
                "L1:CHAN_C",
            ],
        )
        assert result.exit_code == 0

        output_files = list(output_dir_keep.glob("*.gwf"))
        frames = list(gwframe.read_frames(str(output_files[0])))
        assert "L1:CHAN_A" in frames[0]
        assert "L1:CHAN_C" in frames[0]
        assert "L1:CHAN_B" not in frames[0]

    def test_combine_errors(self, single_frame_file, tmp_path):
        """Test combine error handling."""
        output_dir = tmp_path / "output"

        # Test less than 2 sources
        result = runner.invoke(
            app, ["combine", str(single_frame_file), "-o", str(output_dir)]
        )
        assert result.exit_code != 0
        assert "at least 2" in result.stdout.lower()


class TestRecompressCommand:
    """Tests for gwframe recompress command."""

    def test_recompress_basic(self, single_frame_file, tmp_path):
        """Test basic recompress command."""
        output_dir = tmp_path / "output"

        result = runner.invoke(
            app,
            [
                "recompress",
                str(single_frame_file),
                "-o",
                str(output_dir),
                "-c",
                "GZIP",
                "-l",
                "9",
            ],
        )

        assert result.exit_code == 0, result.stdout
        assert (output_dir / single_frame_file.name).exists()

        # Verify data integrity after recompression
        output_file = output_dir / single_frame_file.name
        original_data = gwframe.read(str(single_frame_file), "L1:CHAN1")
        recompressed_data = gwframe.read(str(output_file), "L1:CHAN1")
        assert np.allclose(original_data.array, recompressed_data.array)

    def test_recompress_in_place(self, single_frame_file, tmp_path):
        """Test recompress with --in-place."""
        test_file = tmp_path / "test.gwf"
        shutil.copy(single_frame_file, test_file)

        # Read original data
        original_data = gwframe.read(str(test_file), "L1:CHAN1")

        result = runner.invoke(app, ["recompress", str(test_file), "-i", "-c", "RAW"])

        assert result.exit_code == 0, result.stdout

        # Verify data integrity after in-place recompression
        recompressed_data = gwframe.read(str(test_file), "L1:CHAN1")
        assert np.allclose(original_data.array, recompressed_data.array)


class TestCLIVsAPI:
    """Tests comparing CLI results with direct API calls."""

    def test_rename_cli_matches_api(self, single_frame_file, tmp_path):
        """Test that CLI rename produces same results as API."""
        cli_output = tmp_path / "cli_output"
        api_output = tmp_path / "api_output"

        channel_map = {"L1:CHAN1": "TEST:RENAMED1"}

        # Run via CLI
        result = runner.invoke(
            app,
            [
                "rename",
                str(single_frame_file),
                "-o",
                str(cli_output),
                "-m",
                "L1:CHAN1=>TEST:RENAMED1",
            ],
        )
        assert result.exit_code == 0

        # Run via API
        gwframe.rename_channels(
            str(single_frame_file), str(api_output), channel_map=channel_map
        )

        # Compare results
        cli_file = cli_output / single_frame_file.name
        api_file = api_output / single_frame_file.name

        cli_channels = sorted(gwframe.get_channels(str(cli_file)))
        api_channels = sorted(gwframe.get_channels(str(api_file)))
        assert cli_channels == api_channels

        # Compare data
        cli_data = gwframe.read(str(cli_file), "TEST:RENAMED1")
        api_data = gwframe.read(str(api_file), "TEST:RENAMED1")
        assert np.allclose(cli_data.array, api_data.array)

    def test_drop_cli_matches_api(self, single_frame_file, tmp_path):
        """Test that CLI drop produces same results as API."""
        cli_output = tmp_path / "cli_output"
        api_output = tmp_path / "api_output"

        # Run via CLI
        result = runner.invoke(
            app,
            ["drop", str(single_frame_file), "-o", str(cli_output), "-c", "L1:CHAN1"],
        )
        assert result.exit_code == 0

        # Run via API
        gwframe.drop_channels(
            str(single_frame_file), str(api_output), channels_to_drop=["L1:CHAN1"]
        )

        # Compare results
        cli_file = cli_output / single_frame_file.name
        api_file = api_output / single_frame_file.name

        cli_channels = sorted(gwframe.get_channels(str(cli_file)))
        api_channels = sorted(gwframe.get_channels(str(api_file)))
        assert cli_channels == api_channels

    def test_resize_cli_matches_api(self, multi_frame_file, tmp_path, sample_data):
        """Test that CLI resize produces same results as API."""
        cli_output = tmp_path / "cli_output"
        api_output = tmp_path / "api_output"
        target_duration = sample_data["duration"] / 2

        # Run via CLI
        result = runner.invoke(
            app,
            [
                "resize",
                str(multi_frame_file),
                "-o",
                str(cli_output),
                "-d",
                str(target_duration),
            ],
        )
        assert result.exit_code == 0

        # Run via API
        gwframe.resize_frames(
            str(multi_frame_file), str(api_output), target_duration=target_duration
        )

        # Compare results
        cli_file = cli_output / multi_frame_file.name
        api_file = api_output / multi_frame_file.name

        cli_frames = list(gwframe.read_frames(str(cli_file)))
        api_frames = list(gwframe.read_frames(str(api_file)))
        assert len(cli_frames) == len(api_frames)

        # Compare frame data
        for cli_frame, api_frame in zip(cli_frames, api_frames):
            assert abs(cli_frame.t0 - api_frame.t0) < 1e-9
            assert abs(cli_frame.duration - api_frame.duration) < 1e-9


class TestErrorHandling:
    """Tests for CLI error handling."""

    def test_missing_output_dir(self, single_frame_file):
        """Test that missing output directory is caught."""
        result = runner.invoke(
            app, ["rename", str(single_frame_file), "-m", "L1:CHAN1=>TEST:RENAMED"]
        )

        assert result.exit_code != 0
        assert "output" in result.stdout.lower() or "required" in result.stdout.lower()

    def test_invalid_mapping_format(self, single_frame_file, tmp_path):
        """Test that invalid mapping format is caught."""
        output_dir = tmp_path / "output"

        result = runner.invoke(
            app,
            [
                "rename",
                str(single_frame_file),
                "-o",
                str(output_dir),
                "-m",
                "INVALID_MAPPING",
            ],
        )

        assert result.exit_code != 0
        assert "invalid" in result.stdout.lower()

    def test_no_files_found(self, tmp_path):
        """Test handling when no files are found."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        output_dir = tmp_path / "output"

        result = runner.invoke(
            app,
            ["rename", str(empty_dir), "-o", str(output_dir), "-m", "A=>B"],
        )

        assert result.exit_code != 0
        assert "no files" in result.stdout.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
