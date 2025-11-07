# Copyright (c) 2025, California Institute of Technology and contributors
#
# You should have received a copy of the licensing terms for this
# software included in the file "LICENSE" located in the top-level
# directory of this package. If you did not, you can view a copy at
# https://git.ligo.org/patrick.godwin/gwframe/-/raw/main/LICENSE

"""Read functions for GWF files."""

from __future__ import annotations

from os import PathLike, fspath
from typing import TYPE_CHECKING, Generator, overload

if TYPE_CHECKING:
    from typing import BinaryIO

import numpy as np

from . import _core  # type: ignore[attr-defined]
from .errors import ChannelNotFoundError, InvalidTimeRangeError
from .inspect import get_info
from .types import TimeSeries
from .write import Frame


@overload
def read(
    source: str | PathLike[str] | BinaryIO,
    channel: str,
    frame_index: int = 0,
    *,
    validate_checksum: bool = False,
    start: float | None = None,
    end: float | None = None,
) -> TimeSeries: ...


@overload
def read(
    source: str | PathLike[str] | BinaryIO,
    channel: None,
    frame_index: int = 0,
    *,
    validate_checksum: bool = False,
    start: float | None = None,
    end: float | None = None,
) -> dict[str, TimeSeries]: ...


@overload
def read(
    source: str | PathLike[str] | BinaryIO,
    channel: list[str],
    frame_index: int = 0,
    *,
    validate_checksum: bool = False,
    start: float | None = None,
    end: float | None = None,
) -> dict[str, TimeSeries]: ...


def read(
    source: str | PathLike[str] | BinaryIO,
    channel: str | None | list[str] = None,
    frame_index: int = 0,
    *,
    validate_checksum: bool = False,
    start: float | None = None,
    end: float | None = None,
) -> TimeSeries | dict[str, TimeSeries]:
    """
    Read channel data from a GWF file or file-like object.

    Parameters
    ----------
    source : str, path-like, or file-like object
        Either a path to the GWF file (str or PathLike), or a file-like object
        with a .read() method (e.g., open('file.gwf', 'rb'), BytesIO)
    channel : str, None, or list[str], optional
        Channel(s) to read:
        - str: Read single channel (e.g., 'L1:GWOSC-16KHZ_R1_STRAIN')
        - None: Read all channels from the frame (default)
        - list[str]: Read specific list of channels
    frame_index : int, optional
        Index of the frame to read from (default: 0).
        Mutually exclusive with start/end parameters.
    validate_checksum : bool, optional
        Validate frame file checksums before reading (default: False).
        When enabled, performs file-level checksum validation which requires
        reading the entire frame file. Disabled by default for performance.
    start : float, optional
        GPS start time for time-based slicing. Must be used with end parameter.
        When specified, reads and stitches all frames overlapping [start, end).
        Mutually exclusive with frame_index parameter.
    end : float, optional
        GPS end time for time-based slicing. Must be used with start parameter.
        When specified, reads and stitches all frames overlapping [start, end).
        Mutually exclusive with frame_index parameter.

    Returns
    -------
    data : TimeSeries or dict[str, TimeSeries]
        - If channel is a str: returns TimeSeries for that channel
        - If channel is None or list[str]: returns dict mapping channel names
          to TimeSeries

    Examples
    --------
    >>> # Read single channel from file path
    >>> data = gwframe.read('data.gwf', 'L1:GWOSC-16KHZ_R1_STRAIN')
    >>> print(f"Read {len(data.array)} samples at {data.sample_rate} Hz")
    >>> print(f"Time range: {data.t0} to {data.t0 + data.duration}")

    >>> # Read all channels
    >>> all_data = gwframe.read('data.gwf', channel=None)
    >>> print(f"Found {len(all_data)} channels: {list(all_data.keys())}")

    >>> # Read specific list of channels
    >>> channels = ['L1:STRAIN', 'L1:LSC-DARM_IN1']
    >>> data_dict = gwframe.read('data.gwf', channels)
    >>> for ch, ts in data_dict.items():
    ...     print(f"{ch}: {len(ts.array)} samples")

    >>> # Read from file object
    >>> with open('data.gwf', 'rb') as f:
    ...     data = gwframe.read(f, 'L1:GWOSC-16KHZ_R1_STRAIN')

    >>> # Read from BytesIO
    >>> from io import BytesIO
    >>> data = gwframe.read(BytesIO(gwf_bytes), 'L1:STRAIN')

    >>> # Time-based slicing (reads and stitches multiple frames)
    >>> data = gwframe.read('multi_frame.gwf', 'L1:STRAIN',
    ...                     start=1234567890.0, end=1234567900.0)
    >>> print(
    ...     f"Read {data.duration} seconds from {data.t0} to "
    ...     f"{data.t0 + data.duration}"
    ... )

    Notes
    -----
    When using time-based slicing (start/end parameters), this function
    automatically finds, reads, and stitches together all frames that overlap
    with the requested time range. The returned data is sliced to the exact
    [start, end) interval.

    When reading from file-like objects, the entire file is loaded
    into memory.
    """
    # Step 0: Validate parameters
    if (start is None) != (end is None):
        msg = "start and end must be specified together"
        raise ValueError(msg)

    if start is not None and frame_index != 0:
        msg = "start/end parameters are mutually exclusive with frame_index"
        raise ValueError(msg)

    # Step 1: Handle file-like objects early - delegate to read_bytes
    if hasattr(source, "read"):
        gwf_bytes = source.read()
        return read_bytes(
            gwf_bytes,
            channel,
            frame_index,
            validate_checksum=validate_checksum,
            start=start,
            end=end,
        )

    # Step 2: Validate source is a path-like object and convert to string
    try:
        source_path = fspath(source)
    except TypeError:
        msg = f"source must be str, path-like, or file-like object, got {type(source)}"
        raise TypeError(msg) from None

    # Step 3a: For validation or multi-channel (not time-slicing),
    # use read_bytes path (needs full file)
    if validate_checksum or channel is None or isinstance(channel, list):
        with open(source_path, "rb") as f:
            file_bytes = f.read()
        return read_bytes(
            file_bytes,
            channel,
            frame_index,
            validate_checksum=validate_checksum,
            start=start,
            end=end,
        )

    # Step 3b: For time-based slicing with single channel, use streaming
    # (memory efficient - doesn't load full file)
    if start is not None:
        assert end is not None
        return _read_streaming_slice(source_path, channel, start, end)

    # Step 4: Fast path for single channel without validation
    if not isinstance(channel, str):
        msg = f"channel must be str, None, or list[str], got {type(channel)}"
        raise TypeError(msg)

    stream = _core.IFrameFStream(source_path)
    toc = stream.get_toc()

    # Use TOC to determine channel type
    proc_channels = toc.get_proc()
    adc_channels = toc.get_adc()
    sim_channels = toc.get_sim()

    # Get frame start time from TOC
    time_s = toc.get_time_s()
    time_ns = toc.get_time_ns()
    frame_t0 = float(time_s[frame_index]) + float(time_ns[frame_index]) * 1e-9

    if channel in proc_channels:
        channel_type = "proc"
        fr_data = stream.read_fr_proc_data(frame_index, channel)
    elif channel in adc_channels:
        channel_type = "adc"
        fr_data = stream.read_fr_adc_data(frame_index, channel)
    elif channel in sim_channels:
        channel_type = "sim"
        fr_data = stream.read_fr_sim_data(frame_index, channel)
    else:
        available = [*proc_channels, *adc_channels, *sim_channels]
        raise ChannelNotFoundError(channel, available, source_path)

    # Get the FrVect data vector (usually only one)
    if fr_data.get_data_size() == 0:
        msg = f"No data vectors found for channel '{channel}'"
        raise ValueError(msg)

    vect = fr_data.get_data_vector(0)  # Get first (usually only) vector

    # Extract NumPy array
    array = vect.get_data_uncompressed()

    # Get timing information
    if vect.get_n_dim() > 0:
        dim = vect.get_dim(0)
        dt = dim.dx  # Sample spacing
    else:
        dt = 0.0

    # Calculate data start time (frame start + offset)
    time_offset = fr_data.get_time_offset()
    data_t0 = frame_t0 + time_offset

    # Calculate duration and sample rate
    duration = dt * len(array) if dt > 0 else 0.0
    sample_rate = 1.0 / dt if dt > 0 else 0.0

    # Ensure channel_type is set (helps mypy type narrowing)
    assert channel_type is not None

    return TimeSeries(
        array=array,
        name=vect.get_name(),
        dtype=vect.get_type(),
        t0=data_t0,
        dt=dt,
        duration=duration,
        sample_rate=sample_rate,
        unit=vect.get_unit_y(),
        type=channel_type,
    )


def _read_streaming_slice(
    source_path: str, channel: str, start: float, end: float
) -> TimeSeries:
    """
    Read time slice using streaming (memory efficient, like gwpy).

    Instead of loading full file into memory, streams frames and reads
    only those overlapping [start, end).
    """
    stream = _core.IFrameFStream(source_path)

    # Find frame indices overlapping [start, end) using TOC or iteration
    frame_indices = _find_overlapping_frames_streaming(stream, start, end)

    if not frame_indices:
        # Get file time range for helpful error message
        toc = stream.get_toc()
        time_s = toc.get_time_s()
        time_ns = toc.get_time_ns()
        frame_dt = toc.get_dt()
        if len(time_s) > 0:
            file_start = float(time_s[0]) + float(time_ns[0]) * 1e-9
            file_end = file_start + sum(frame_dt)
        else:
            # Empty file
            file_start = file_end = 0.0
        raise InvalidTimeRangeError(start, end, file_start, file_end, source_path)

    # Read overlapping frames
    timeseries_list: list[TimeSeries] = []
    for frame_idx in frame_indices:
        ts = read(source_path, channel, frame_index=frame_idx)
        assert isinstance(ts, TimeSeries)
        timeseries_list.append(ts)

    # Stitch and slice using shared helper
    return _stitch_and_slice_timeseries(timeseries_list, start, end)


def _find_overlapping_frames_streaming(
    stream: _core.IFrameFStream, start: float, end: float
) -> list[int]:
    """Find frame indices overlapping [start, end) using stream."""
    frame_indices = []
    toc = stream.get_toc()
    time_s = toc.get_time_s()
    time_ns = toc.get_time_ns()
    frame_dt = toc.get_dt()

    for i in range(len(time_s)):
        frame_start = float(time_s[i]) + float(time_ns[i]) * 1e-9
        frame_end = frame_start + frame_dt[i]

        # Frame overlaps if: frame_start < end AND frame_end > start
        if frame_start < end and frame_end > start:
            frame_indices.append(i)

    return frame_indices


def _stitch_and_slice_timeseries(
    timeseries_list: list[TimeSeries], start: float, end: float
) -> TimeSeries:
    """Stitch multiple TimeSeries and slice to [start, end) range."""
    # Stitch timeseries together
    if len(timeseries_list) == 1:
        combined_ts = timeseries_list[0]
    else:
        arrays = [ts.array for ts in timeseries_list]
        combined_array = np.concatenate(arrays)

        first_ts = timeseries_list[0]
        combined_duration = sum(ts.duration for ts in timeseries_list)

        combined_ts = TimeSeries(
            array=combined_array,
            name=first_ts.name,
            dtype=first_ts.dtype,
            t0=first_ts.t0,
            dt=first_ts.dt,
            duration=combined_duration,
            sample_rate=first_ts.sample_rate,
            unit=first_ts.unit,
            type=first_ts.type,
        )

    # Slice to exact [start, end) range
    data_start = combined_ts.t0
    data_end = combined_ts.t0 + combined_ts.duration

    if start > data_start:
        start_idx = round((start - data_start) * combined_ts.sample_rate)
    else:
        start_idx = 0

    if end < data_end:
        end_idx = round((end - data_start) * combined_ts.sample_rate)
    else:
        end_idx = len(combined_ts.array)

    # Slice the array
    sliced_array = combined_ts.array[start_idx:end_idx]
    actual_start = combined_ts.t0 + start_idx * combined_ts.dt
    actual_duration = len(sliced_array) * combined_ts.dt

    return TimeSeries(
        array=sliced_array,
        name=combined_ts.name,
        dtype=combined_ts.dtype,
        t0=actual_start,
        dt=combined_ts.dt,
        duration=actual_duration,
        sample_rate=combined_ts.sample_rate,
        unit=combined_ts.unit,
        type=combined_ts.type,
    )


@overload
def read_bytes(
    data: bytes,
    channel: str,
    frame_index: int = 0,
    *,
    validate_checksum: bool = False,
    start: float | None = None,
    end: float | None = None,
) -> TimeSeries: ...


@overload
def read_bytes(
    data: bytes,
    channel: None,
    frame_index: int = 0,
    *,
    validate_checksum: bool = False,
    start: float | None = None,
    end: float | None = None,
) -> dict[str, TimeSeries]: ...


@overload
def read_bytes(
    data: bytes,
    channel: list[str],
    frame_index: int = 0,
    *,
    validate_checksum: bool = False,
    start: float | None = None,
    end: float | None = None,
) -> dict[str, TimeSeries]: ...


def read_bytes(
    data: bytes,
    channel: str | None | list[str] = None,
    frame_index: int = 0,
    *,
    validate_checksum: bool = False,
    start: float | None = None,
    end: float | None = None,
) -> TimeSeries | dict[str, TimeSeries]:
    """
    Read channel data from GWF data in memory (bytes).

    This allows reading GWF data without writing to disk first,
    which is useful when working with data from network streams,
    compressed archives, or in-memory buffers.

    Parameters
    ----------
    data : bytes
        Raw GWF file data as bytes
    channel : str, None, or list[str], optional
        Channel(s) to read:
        - str: Read single channel (e.g., 'L1:GWOSC-16KHZ_R1_STRAIN')
        - None: Read all channels from the frame (default)
        - list[str]: Read specific list of channels
    frame_index : int, optional
        Index of the frame to read from (default: 0)
    validate_checksum : bool, optional
        Validate frame file checksums before reading (default: False).
        When enabled, performs file-level checksum validation which requires
        reading the entire frame file. Disabled by default for performance.

    Returns
    -------
    data : TimeSeries or dict[str, TimeSeries]
        - If channel is a str: returns TimeSeries for that channel
        - If channel is None or list[str]: returns dict mapping channel names
          to TimeSeries

    Examples
    --------
    >>> with open('data.gwf', 'rb') as f:
    ...     gwf_bytes = f.read()
    >>> data = gwframe.read_bytes(gwf_bytes, 'L1:GWOSC-16KHZ_R1_STRAIN')
    >>> print(f"Read {len(data.array)} samples at {data.sample_rate} Hz")

    >>> # Read all channels
    >>> all_data = gwframe.read_bytes(gwf_bytes, channel=None)
    >>> print(f"Found {len(all_data)} channels")

    >>> import io
    >>> from io import BytesIO
    >>> data = gwframe.read_bytes(BytesIO(gwf_bytes).read(), 'L1:STRAIN')

    Notes
    -----
    This function uses frameCPP's MemoryBuffer internally to read
    from memory without writing to disk.
    """
    # Verify input is bytes
    if not isinstance(data, bytes):
        msg = f"data must be bytes, got {type(data)}"
        raise TypeError(msg)

    # Validate time-based slicing parameters
    if (start is None) != (end is None):
        msg = "start and end must be specified together"
        raise ValueError(msg)

    if start is not None and frame_index != 0:
        msg = "start/end parameters are mutually exclusive with frame_index"
        raise ValueError(msg)

    # Handle time-based slicing
    if start is not None:
        # For multi-channel, recursively read each channel with time slicing
        if channel is None or isinstance(channel, list):
            if channel is None:
                proc_ch, adc_ch, sim_ch = _core.enumerate_channels_from_bytes(data, 0)
                channels_to_read = list(proc_ch) + list(adc_ch) + list(sim_ch)
            else:
                channels_to_read = channel

            result: dict[str, TimeSeries] = {}
            for ch in channels_to_read:
                try:
                    ts = read_bytes(
                        data,
                        ch,
                        0,
                        validate_checksum=validate_checksum,
                        start=start,
                        end=end,
                    )
                    assert isinstance(
                        ts, TimeSeries
                    )  # Single channel returns TimeSeries
                    result[ch] = ts
                except (ValueError, RuntimeError):
                    continue
            return result

        # Single channel case - must be a string
        if not isinstance(channel, str):
            msg = f"channel must be str, None, or list[str], got {type(channel)}"
            raise TypeError(msg)

        # Find frames overlapping [start, end) using frame times
        frame_times = _core.get_frame_times_from_bytes(data)

        # Find which frames overlap with [start, end)
        # A frame overlaps if: frame_start < end AND frame_end > start
        frame_indices = [
            i
            for i, (frame_start, frame_duration) in enumerate(frame_times)
            if frame_start < end and (frame_start + frame_duration) > start
        ]

        if not frame_indices:
            # Get file time range for helpful error message
            if frame_times:
                file_start = frame_times[0][0]
                file_end = frame_times[-1][0] + frame_times[-1][1]
            else:
                file_start = file_end = 0.0
            assert start is not None and end is not None
            raise InvalidTimeRangeError(start, end, file_start, file_end)

        # Read and concatenate frames
        timeseries_list: list[TimeSeries] = []
        for frame_idx in frame_indices:
            ts = read_bytes(
                data, channel, frame_idx, validate_checksum=validate_checksum
            )
            assert isinstance(ts, TimeSeries)  # Narrows type for mypy
            timeseries_list.append(ts)

        # Stitch and slice using shared helper
        assert start is not None and end is not None
        return _stitch_and_slice_timeseries(timeseries_list, start, end)

    # Handle multiple channel cases
    if channel is None or isinstance(channel, list):
        # Get list of channels to read
        if channel is None:
            # Read all channels - enumerate from frame
            proc_ch, adc_ch, sim_ch = _core.enumerate_channels_from_bytes(
                data, frame_index
            )
            channels_to_read = list(proc_ch) + list(adc_ch) + list(sim_ch)
        else:
            # channel is a list[str]
            channels_to_read = channel

        # Read each channel and return dict
        channel_dict: dict[str, TimeSeries] = {}
        for ch in channels_to_read:
            try:
                ts = read_bytes(
                    data, ch, frame_index, validate_checksum=validate_checksum
                )
                assert isinstance(ts, TimeSeries)  # Single channel returns TimeSeries
                channel_dict[ch] = ts
            except (ValueError, RuntimeError):
                # Skip channels that fail to read
                continue

        return channel_dict

    # Single channel case (channel is a str)
    if not isinstance(channel, str):
        msg = f"channel must be str, None, or list[str], got {type(channel)}"
        raise TypeError(msg)

    # Validate checksums if requested
    if validate_checksum:
        _core.validate_frame_checksums(data)

    # Try each channel type until one works
    fr_data = None
    channel_type = None

    readers = [
        ("proc", _core.read_proc_from_bytes),
        ("sim", _core.read_sim_from_bytes),
        ("adc", _core.read_adc_from_bytes),
    ]

    for reader_type, reader_func in readers:
        try:
            fr_data = reader_func(data, frame_index, channel)
            channel_type = reader_type
            break
        except (RuntimeError, ValueError):
            continue

    if fr_data is None:
        # Get available channels to provide helpful error
        proc_ch, adc_ch, sim_ch = _core.enumerate_channels_from_bytes(data, frame_index)
        available = list(proc_ch) + list(adc_ch) + list(sim_ch)
        raise ChannelNotFoundError(channel, available)

    # Get the FrVect data vector (usually only one)
    if fr_data.get_data_size() == 0:
        msg = f"No data vectors found for channel '{channel}'"
        raise ValueError(msg)

    vect = fr_data.get_data_vector(0)  # Get first (usually only) vector

    # Extract NumPy array
    array = vect.get_data_uncompressed()

    # Get timing information
    if vect.get_n_dim() > 0:
        dim = vect.get_dim(0)
        dt = dim.dx  # Sample spacing
    else:
        dt = 0.0

    # Get time offset
    time_offset = fr_data.get_time_offset()

    # Read frame header to get GPS start time
    time_s, time_ns = _core.read_frame_gps_time(data, frame_index)
    frame_t0 = float(time_s) + float(time_ns) * 1e-9

    # Calculate data start time (frame start + offset)
    data_t0 = frame_t0 + time_offset

    # Calculate duration and sample rate
    duration = dt * len(array) if dt > 0 else 0.0
    sample_rate = 1.0 / dt if dt > 0 else 0.0

    # Ensure channel_type is set (helps mypy type narrowing)
    assert channel_type is not None

    return TimeSeries(
        array=array,
        name=vect.get_name(),
        dtype=vect.get_type(),
        t0=data_t0,
        dt=dt,
        duration=duration,
        sample_rate=sample_rate,
        unit=vect.get_unit_y(),
        type=channel_type,
    )


def read_frames(filename: str | PathLike[str]) -> Generator[Frame, None, None]:
    """
    Read frames from a GWF file, preserving complete metadata.

    Yields Frame objects that can be written directly to disk with identical
    metadata (frame name, run number, frame number, etc.).

    Parameters
    ----------
    filename : str or path-like
        Path to the GWF file

    Yields
    ------
    frame : Frame
        Frame object containing all channel data with correct sample rates,
        units, types, and original frame metadata

    Examples
    --------
    >>> # Iterate over frames
    >>> for frame in gwframe.read_frames('data.gwf'):
    ...     print(f"Frame {frame.name} at GPS {frame.t0}")

    >>> # Process and write frames
    >>> with gwframe.FrameWriter('output.gwf') as writer:
    ...     for frame in gwframe.read_frames('input.gwf'):
    ...         writer.write_frame(frame)

    >>> # Collect all frames into a list
    >>> frames = list(gwframe.read_frames('data.gwf'))
    >>> print(f"Read {len(frames)} frames")

    See Also
    --------
    read : Read channel data from frames
    Frame : Frame object for creating and manipulating frames
    FrameWriter : Context manager for writing frames to files
    """
    # Convert to string path
    filename_str = fspath(filename) if not isinstance(filename, str) else filename

    # Get file metadata
    file_info = get_info(filename_str)

    for frame_info in file_info.frames:
        # Read all channels for this frame
        channel_data = read(filename_str, channel=None, frame_index=frame_info.index)
        assert isinstance(channel_data, dict)  # channel=None returns dict

        # Create Frame with preserved metadata
        frame = Frame(
            t0=frame_info.t0,
            duration=frame_info.duration,
            name=frame_info.name,
            run=frame_info.run,
            frame_number=frame_info.frame_number,
        )

        # Add all channels with their metadata
        for channel_name, ts in channel_data.items():
            frame.add_channel(
                channel=channel_name,
                data=ts.array,
                sample_rate=ts.sample_rate,
                unit=ts.unit,
                channel_type=ts.type,
            )

        yield frame
