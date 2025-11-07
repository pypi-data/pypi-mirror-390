# Copyright (c) 2025, California Institute of Technology and contributors
#
# You should have received a copy of the licensing terms for this
# software included in the file "LICENSE" located in the top-level
# directory of this package. If you did not, you can view a copy at
# https://git.ligo.org/patrick.godwin/gwframe/-/raw/main/LICENSE

"""Core operations for manipulating GWF files."""

from __future__ import annotations

import shutil
import tempfile
from collections import defaultdict
from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from .inspect import get_info
from .read import read, read_frames
from .types import Compression, TimeSeries
from .write import Frame, FrameWriter

if TYPE_CHECKING:
    from collections.abc import Sequence


def _handle_in_place(input_files: list[Path], output_files: list[str]) -> list[str]:
    """
    Move output files back to input locations for in-place modification.

    Parameters
    ----------
    input_files : list[Path]
        Original input file paths
    output_files : list[str]
        Temporary output file paths

    Returns
    -------
    final_paths : list[str]
        Final file paths (same as input_files)
    """
    for input_file, output_file in zip(input_files, output_files):
        shutil.move(output_file, str(input_file))
    return [str(f) for f in input_files]


def _process_files_with_operation(
    input_files: str | PathLike[str] | Sequence[str | PathLike[str]],
    output_dir: str | PathLike[str] | None,
    file_operation,
    *,
    in_place: bool = False,
) -> list[str]:
    """
    Common wrapper for file processing operations.

    Handles file management: input normalization, temp directories for in-place
    operations, and moving files back to original locations.

    Parameters
    ----------
    input_files : str, path-like, or sequence of str/path-like
        Input GWF file(s) to process
    output_dir : str, path-like, or None
        Directory where output files will be written.
        Required if in_place=False, ignored if in_place=True.
    in_place : bool
        If True, modify files in place using a temporary directory
    file_operation : callable
        Function that processes a single file. Called as
        file_operation(input_file_path, output_file_path).
        Should read frames from input_file_path, process them,
        and write to output_file_path.

    Returns
    -------
    output_files : list[str]
        List of output file paths created
    """
    # Validate mutually exclusive options
    if in_place and output_dir is not None:
        msg = "in_place and output_dir are mutually exclusive"
        raise ValueError(msg)

    if not in_place and output_dir is None:
        msg = "output_dir must be specified when in_place=False"
        raise ValueError(msg)

    # Normalize input to list of Paths
    if isinstance(input_files, str | PathLike):
        input_files = [input_files]
    input_file_paths = [Path(f) for f in input_files]

    # Set up output directory (temp for in-place, or user-specified)
    if in_place:
        temp_dir_obj = tempfile.TemporaryDirectory()
        output_dir = Path(temp_dir_obj.name)
    else:
        temp_dir_obj = None
        assert output_dir is not None  # Guaranteed by validation above
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    try:
        output_files = []

        # Process each input file
        for input_file in input_file_paths:
            output_file = output_dir / input_file.name
            output_files.append(str(output_file))

            # Call the file operation function
            file_operation(str(input_file), str(output_file))

        # Move files back to original locations if in-place
        if in_place:
            output_files = _handle_in_place(input_file_paths, output_files)

        return output_files

    finally:
        # Cleanup temp directory
        if temp_dir_obj is not None:
            temp_dir_obj.cleanup()


def rename_channels(
    input_files: str | PathLike[str] | Sequence[str | PathLike[str]],
    output_dir: str | PathLike[str] | None = None,
    channel_map: dict[str, str] | None = None,
    *,
    in_place: bool = False,
) -> list[str]:
    """
    Rename channels in frame files.

    Parameters
    ----------
    input_files : str, path-like, or sequence of str/path-like
        Input GWF file(s) to process
    output_dir : str, path-like, or None
        Directory where output files will be written.
        Required if in_place=False, ignored if in_place=True.
    channel_map : dict
        Mapping of old channel names to new channel names
    in_place : bool, optional
        If True, modify files in place (default: False)

    Returns
    -------
    output_files : list[str]
        List of output file paths created

    Examples
    --------
    >>> # Write to output directory
    >>> gwframe.rename_channels(
    ...     'input.gwf',
    ...     'output/',
    ...     {'L1:OLD_NAME': 'L1:NEW_NAME'}
    ... )

    >>> # Modify in place
    >>> gwframe.rename_channels(
    ...     'input.gwf',
    ...     channel_map={'L1:OLD_NAME': 'L1:NEW_NAME'},
    ...     in_place=True
    ... )
    """
    if not channel_map:
        msg = "channel_map must be provided and non-empty"
        raise ValueError(msg)

    def _rename_file(input_file, output_file):
        """Process a single file, renaming channels."""
        frames = read_frames(input_file)

        with FrameWriter(output_file) as writer:
            for frame in frames:
                # Rename channels in frame
                for old_name, new_name in channel_map.items():
                    if old_name in frame:
                        frame[new_name] = frame.pop(old_name)
                writer.write_frame(frame)

    return _process_files_with_operation(
        input_files, output_dir, _rename_file, in_place=in_place
    )


def combine_channels(
    input_sources: Sequence[str | PathLike[str]],
    output_dir: str | PathLike[str],
    keep_channels: Sequence[str] | None = None,
    drop_channels: Sequence[str] | None = None,
) -> list[str]:
    """
    Combine channels from multiple frame sources into single files.

    Takes N sources (all files or all directories) covering the same time ranges
    and combines their channels. Sources are matched by time range.

    Parameters
    ----------
    input_sources : sequence of str or path-like
        List of N source files or N source directories to combine.
        All sources must be the same type (all files or all directories).
    output_dir : str or path-like
        Directory where output files will be written
    keep_channels : sequence of str, optional
        If specified, only include these channels in the output.
        Mutually exclusive with drop_channels.
    drop_channels : sequence of str, optional
        If specified, exclude these channels from the output.
        Mutually exclusive with keep_channels.

    Returns
    -------
    output_files : list[str]
        List of output file paths created

    Examples
    --------
    >>> # Combine 2 files covering the same time range
    >>> gwframe.combine_channels(['file1.gwf', 'file2.gwf'], 'output/')

    >>> # Combine and keep only specific channels
    >>> gwframe.combine_channels(
    ...     ['file1.gwf', 'file2.gwf'], 'output/',
    ...     keep_channels=['L1:STRAIN', 'L1:LSC']
    ... )

    >>> # Combine and drop specific channels
    >>> gwframe.combine_channels(
    ...     ['dir1/', 'dir2/'], 'output/',
    ...     drop_channels=['L1:UNWANTED']
    ... )

    Notes
    -----
    All sources must have matching frame structures (same times and durations).
    Raises detailed error messages if frames don't align.
    """
    if len(input_sources) < 2:
        msg = "combine_channels requires at least 2 sources"
        raise ValueError(msg)

    if keep_channels is not None and drop_channels is not None:
        msg = "keep_channels and drop_channels are mutually exclusive"
        raise ValueError(msg)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Check if sources are files or directories
    source_paths = [Path(s) for s in input_sources]
    are_files = [p.is_file() for p in source_paths]
    are_dirs = [p.is_dir() for p in source_paths]

    if not (all(are_files) or all(are_dirs)):
        msg = "All sources must be the same type (all files or all directories)"
        raise ValueError(msg)

    if all(are_files):
        return _combine_files(source_paths, output_dir, keep_channels, drop_channels)
    return _combine_directories(source_paths, output_dir, keep_channels, drop_channels)


def _combine_files(
    source_files: Sequence[Path],
    output_dir: Path,
    keep_channels: Sequence[str] | None = None,
    drop_channels: Sequence[str] | None = None,
) -> list[str]:
    """Combine N files covering the same time range."""
    # Read all frames from all sources
    all_frames_list = [[*read_frames(str(f))] for f in source_files]

    # Validate all files have the same frame count
    base_frames = all_frames_list[0]
    for i, frames in enumerate(all_frames_list[1:], start=1):
        if len(frames) != len(base_frames):
            msg = (
                f"Frame count mismatch: {source_files[0].name} has "
                f"{len(base_frames)} frames, but {source_files[i].name} has "
                f"{len(frames)} frames"
            )
            raise ValueError(msg)

    # Validate frame timing matches
    for frame_idx in range(len(base_frames)):
        base_frame = base_frames[frame_idx]
        for i, frames in enumerate(all_frames_list[1:], start=1):
            other_frame = frames[frame_idx]
            if abs(base_frame.t0 - other_frame.t0) > 1e-9:
                msg = (
                    f"Frame {frame_idx} time mismatch: "
                    f"{source_files[0].name} starts at {base_frame.t0}, "
                    f"but {source_files[i].name} starts at {other_frame.t0}"
                )
                raise ValueError(msg)

            if abs(base_frame.duration - other_frame.duration) > 1e-9:
                msg = (
                    f"Frame {frame_idx} duration mismatch: "
                    f"{source_files[0].name} has {base_frame.duration}s, "
                    f"but {source_files[i].name} has {other_frame.duration}s"
                )
                raise ValueError(msg)

    # Convert keep/drop to sets for efficient lookup
    keep_set = set(keep_channels) if keep_channels else None
    drop_set = set(drop_channels) if drop_channels else None

    # All validation passed - combine channels
    output_file = output_dir / f"combined_{source_files[0].name}"
    output_files = [str(output_file)]

    with FrameWriter(str(output_file)) as writer:
        for frame_idx in range(len(base_frames)):
            # Start with the base frame
            combined_frame = base_frames[frame_idx]

            # Add channels from all other sources
            for frames in all_frames_list[1:]:
                other_frame = frames[frame_idx]
                # Check for duplicate channels
                duplicates = set(combined_frame.keys()) & set(other_frame.keys())
                if duplicates:
                    msg = f"Duplicate channels found: {duplicates}"
                    raise ValueError(msg)
                combined_frame.update(other_frame)

            # Apply channel filtering
            if keep_set is not None:
                for channel_name in list(combined_frame.keys()):
                    if channel_name not in keep_set:
                        del combined_frame[channel_name]
            elif drop_set is not None:
                for channel_name in drop_set:
                    if channel_name in combined_frame:
                        del combined_frame[channel_name]

            writer.write_frame(combined_frame)

    return output_files


def _combine_directories(
    source_dirs: Sequence[Path],
    output_dir: Path,
    keep_channels: Sequence[str] | None = None,
    drop_channels: Sequence[str] | None = None,
) -> list[str]:
    """Combine N directories with matching frame sets."""
    # Get all GWF files from each directory
    all_files = []
    for source_dir in source_dirs:
        files = sorted(source_dir.glob("*.gwf"))
        if not files:
            msg = f"No .gwf files found in {source_dir}"
            raise ValueError(msg)
        all_files.append(files)

    # Group files by time range across all directories
    time_to_files = defaultdict(list)

    for dir_idx, files in enumerate(all_files):
        for file_path in files:
            info = get_info(str(file_path))
            # Use first frame's time as key
            # (assuming one frame per file or consistent structure)
            if info.frames:
                frame = info.frames[0]
                time_key = (frame.t0, frame.duration)
                time_to_files[time_key].append((dir_idx, file_path))

    # Validate that each time range has exactly one file from each directory
    for time_key, file_list in time_to_files.items():
        dir_indices = {dir_idx for dir_idx, _ in file_list}
        if len(dir_indices) != len(source_dirs):
            missing_dirs = set(range(len(source_dirs))) - dir_indices
            t0, duration = time_key
            missing_names = [str(source_dirs[i]) for i in missing_dirs]
            msg = (
                f"Time range [{t0}, {t0 + duration}) missing from directories: "
                f"{', '.join(missing_names)}"
            )
            raise ValueError(msg)

    # Combine files for each time range
    output_files = []

    for time_key in sorted(time_to_files.keys()):
        file_list = time_to_files[time_key]
        # Sort by directory index to maintain consistent order
        file_list.sort(key=lambda x: x[0])
        source_files = [Path(f) for _, f in file_list]

        # Use _combine_files to do the actual combination
        combined = _combine_files(
            source_files, output_dir, keep_channels, drop_channels
        )
        output_files.extend(combined)

    return output_files


def drop_channels(
    input_files: str | PathLike[str] | Sequence[str | PathLike[str]],
    output_dir: str | PathLike[str] | None = None,
    channels_to_drop: Sequence[str] | None = None,
    *,
    in_place: bool = False,
) -> list[str]:
    """
    Remove specified channels from frame files.

    Parameters
    ----------
    input_files : str, path-like, or sequence of str/path-like
        Input GWF file(s) to process
    output_dir : str, path-like, or None
        Directory where output files will be written.
        Required if in_place=False. Mutually exclusive with in_place=True.
    channels_to_drop : sequence of str
        List of channel names to remove
    in_place : bool, optional
        If True, modify files in place (default: False)

    Returns
    -------
    output_files : list[str]
        List of output file paths created

    Examples
    --------
    >>> gwframe.drop_channels(
    ...     'input.gwf',
    ...     'output/',
    ...     ['L1:UNWANTED_CHANNEL']
    ... )

    >>> # In place
    >>> gwframe.drop_channels(
    ...     'input.gwf',
    ...     channels_to_drop=['L1:UNWANTED_CHANNEL'],
    ...     in_place=True
    ... )
    """
    if not channels_to_drop:
        msg = "channels_to_drop must be provided and non-empty"
        raise ValueError(msg)

    def _drop_file(input_file, output_file):
        """Process a single file, dropping specified channels."""
        frames = read_frames(input_file)
        channels_set = set(channels_to_drop)

        with FrameWriter(output_file) as writer:
            for frame in frames:
                # Drop channels from frame
                for channel_name in channels_set:
                    if channel_name in frame:
                        del frame[channel_name]
                writer.write_frame(frame)

    return _process_files_with_operation(
        input_files, output_dir, _drop_file, in_place=in_place
    )


def resize_frames(
    input_files: str | PathLike[str] | Sequence[str | PathLike[str]],
    output_dir: str | PathLike[str] | None = None,
    target_duration: float | None = None,
    *,
    in_place: bool = False,
) -> list[str]:
    """
    Resize frames to a different duration (e.g., 64s frames to 4s frames).

    Parameters
    ----------
    input_files : str, path-like, or sequence of str/path-like
        Input GWF file(s) to process
    output_dir : str or path-like, optional
        Directory where output files will be written.
        Required if in_place=False. Ignored if in_place=True.
    target_duration : float
        Target frame duration in seconds
    in_place : bool, optional
        If True, modify files in place (default: False)

    Returns
    -------
    output_files : list[str]
        List of output file paths created

    Examples
    --------
    >>> # Split 64-second frames into 4-second frames
    >>> gwframe.resize_frames('input.gwf', 'output/', target_duration=4.0)

    >>> # Split frames in place
    >>> gwframe.resize_frames('input.gwf', target_duration=4.0, in_place=True)

    Notes
    -----
    When splitting frames (target_duration < source_duration), data is divided
    evenly. When merging frames (target_duration > source_duration), consecutive
    frames are combined.
    """
    if target_duration is None or target_duration <= 0:
        msg = "target_duration must be a positive number"
        raise ValueError(msg)

    def _resize_file(input_file, output_file):
        """Process a single file, resizing frames."""
        frames = read_frames(input_file)

        with FrameWriter(output_file) as writer:
            frame_number = 0

            for frame in frames:
                source_t0 = frame.t0
                source_duration = frame.duration

                # Calculate how many target frames fit in this source frame
                num_splits = int(source_duration / target_duration)

                if num_splits >= 1:
                    # Split into smaller frames
                    for split_idx in range(num_splits):
                        split_t0 = source_t0 + split_idx * target_duration

                        new_frame = Frame(
                            t0=split_t0,
                            duration=target_duration,
                            name=frame.name,
                            run=frame.run,
                            frame_number=frame_number,
                        )

                        # Slice data for this split
                        for channel_name, ts in frame.items():
                            start_sample = int(
                                split_idx * target_duration * ts.sample_rate
                            )
                            end_sample = int(
                                (split_idx + 1) * target_duration * ts.sample_rate
                            )
                            sliced_data = ts.array[start_sample:end_sample]

                            new_frame.add_channel(
                                channel_name,
                                sliced_data,
                                ts.sample_rate,
                                unit=ts.unit,
                                channel_type=ts.type,
                            )

                        writer.write_frame(new_frame)
                        frame_number += 1
                else:
                    # Keep original frame (target_duration >= source_duration)
                    frame.frame_number = frame_number
                    writer.write_frame(frame)
                    frame_number += 1

    return _process_files_with_operation(
        input_files, output_dir, _resize_file, in_place=in_place
    )


def impute_missing_data(
    input_files: str | PathLike[str] | Sequence[str | PathLike[str]],
    output_dir: str | PathLike[str] | None = None,
    replace_value: float = np.nan,
    fill_value: float = 0.0,
    channels: Sequence[str] | None = None,
    *,
    in_place: bool = False,
) -> list[str]:
    """
    Replace specific values in frame file channels with a fill value.

    Parameters
    ----------
    input_files : str, path-like, or sequence of str/path-like
        Input GWF file(s) to process
    output_dir : str, path-like, or None
        Directory where output files will be written.
        Required if in_place=False. Mutually exclusive with in_place=True.
    replace_value : float, optional
        Value to replace (default: NaN). Can be NaN or any numeric value.
    fill_value : float, optional
        Value to use for replacement (default: 0.0). Will be cast to appropriate dtype.
    channels : sequence of str, optional
        If specified, only impute these channels. Otherwise imputes all channels.
    in_place : bool, optional
        If True, modify files in place (default: False)

    Returns
    -------
    output_files : list[str]
        List of output file paths created

    Examples
    --------
    >>> # Replace NaNs with 0 in all channels
    >>> gwframe.impute_missing_data('input.gwf', 'output/')

    >>> # In place
    >>> gwframe.impute_missing_data('input.gwf', in_place=True)

    >>> # Replace specific value in specific channels
    >>> gwframe.impute_missing_data(
    ...     'input.gwf', 'output/',
    ...     replace_value=-999.0,
    ...     fill_value=0.0,
    ...     channels=['L1:STRAIN']
    ... )
    """
    channels_set = set(channels) if channels else None
    is_nan_replacement = np.isnan(replace_value)

    def _impute_file(input_file, output_file):
        """Process a single file, imputing missing data."""
        frames = read_frames(input_file)

        with FrameWriter(output_file) as writer:
            for frame in frames:
                # Determine which channels to impute
                if channels_set is not None:
                    channels_to_impute = channels_set & set(frame.keys())
                else:
                    channels_to_impute = set(frame.keys())

                # Process each channel
                for channel_name in channels_to_impute:
                    ts = frame[channel_name]
                    data = ts.array.copy()
                    # Cast fill_value to appropriate dtype and replace
                    fill = np.array(fill_value).astype(data.dtype)
                    if is_nan_replacement:
                        data = np.where(np.isnan(data), fill, data)
                    else:
                        data = np.where(data == replace_value, fill, data)

                    frame[channel_name] = TimeSeries(
                        array=data,
                        name=ts.name,
                        dtype=ts.dtype,
                        t0=ts.t0,
                        dt=ts.dt,
                        duration=ts.duration,
                        sample_rate=ts.sample_rate,
                        unit=ts.unit,
                        type=ts.type,
                    )

                writer.write_frame(frame)

    return _process_files_with_operation(
        input_files, output_dir, _impute_file, in_place=in_place
    )


def replace_channels(
    base_files: str | PathLike[str] | Sequence[str | PathLike[str]],
    update_files: str | PathLike[str] | Sequence[str | PathLike[str]],
    output_dir: str | PathLike[str],
    channels_to_replace: Sequence[str] | None = None,
) -> list[str]:
    """
    Replace data in channels with updated versions from another frame file.

    Parameters
    ----------
    base_files : str, path-like, or sequence of str/path-like
        Base GWF file(s) to process
    update_files : str, path-like, or sequence of str/path-like
        GWF file(s) containing updated channel data
    output_dir : str or path-like
        Directory where output files will be written
    channels_to_replace : sequence of str, optional
        List of channel names to replace. If None, replaces all channels
        found in update_files.

    Returns
    -------
    output_files : list[str]
        List of output file paths created

    Examples
    --------
    >>> gwframe.replace_channels(
    ...     'base.gwf',
    ...     'updated.gwf',
    ...     'output/',
    ...     ['L1:STRAIN']
    ... )
    """
    if isinstance(base_files, str | PathLike):
        base_files = [base_files]
    if isinstance(update_files, str | PathLike):
        update_files = [update_files]

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_files = []

    for base_file in base_files:
        output_file = output_dir / Path(base_file).name
        output_files.append(str(output_file))

        base_frames = read_frames(base_file)

        with FrameWriter(str(output_file)) as writer:
            for frame in base_frames:
                t0 = frame.t0
                duration = frame.duration

                # Read update data from matching time range
                update_data: dict[str, TimeSeries] = {}
                for update_file in update_files:
                    try:
                        data: dict[str, TimeSeries] = read(
                            update_file, channel=None, start=t0, end=t0 + duration
                        )
                        update_data.update(data)
                    except (ValueError, FileNotFoundError):
                        continue

                # Determine which channels to replace
                if channels_to_replace is None:
                    channels_to_replace_set = set(update_data.keys())
                else:
                    channels_to_replace_set = set(channels_to_replace)

                # Replace specified channels with update data
                for channel_name in channels_to_replace_set:
                    if channel_name in update_data:
                        frame[channel_name] = update_data[channel_name]

                # Add any new channels from update data
                for channel_name, ts in update_data.items():
                    if channel_name not in frame:
                        frame[channel_name] = ts

                writer.write_frame(frame)

    return output_files


def recompress_frames(
    input_files: str | PathLike[str] | Sequence[str | PathLike[str]],
    output_dir: str | PathLike[str] | None = None,
    compression: int = Compression.ZERO_SUPPRESS_OTHERWISE_GZIP,
    compression_level: int = 6,
    *,
    in_place: bool = False,
) -> list[str]:
    """
    Rewrite frame files with different compression settings.

    Parameters
    ----------
    input_files : str, path-like, or sequence of str/path-like
        Input GWF file(s) to process
    output_dir : str or path-like, optional
        Directory where output files will be written.
        Required if in_place=False. Ignored if in_place=True.
    compression : int
        Compression scheme (e.g., Compression.RAW, Compression.GZIP)
    compression_level : int, optional
        Compression level 0-9 (default: 6)
    in_place : bool, optional
        If True, modify files in place (default: False)

    Returns
    -------
    output_files : list[str]
        List of output file paths created

    Examples
    --------
    >>> # Remove compression
    >>> gwframe.recompress_frames('input.gwf', 'output/',
    ...                           compression=gwframe.Compression.RAW)

    >>> # Maximum compression, in place
    >>> gwframe.recompress_frames('input.gwf',
    ...                           compression=gwframe.Compression.GZIP,
    ...                           compression_level=9,
    ...                           in_place=True)
    """

    def _recompress_file(input_file, output_file):
        """Process a single file, rewriting with different compression."""
        frames = read_frames(input_file)

        with FrameWriter(
            output_file, compression=compression, compression_level=compression_level
        ) as writer:
            for frame in frames:
                writer.write_frame(frame)

    return _process_files_with_operation(
        input_files, output_dir, _recompress_file, in_place=in_place
    )
