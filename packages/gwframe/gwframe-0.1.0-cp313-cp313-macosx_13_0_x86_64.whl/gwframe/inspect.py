# Copyright (c) 2025, California Institute of Technology and contributors
#
# You should have received a copy of the licensing terms for this
# software included in the file "LICENSE" located in the top-level
# directory of this package. If you did not, you can view a copy at
# https://git.ligo.org/patrick.godwin/gwframe/-/raw/main/LICENSE

"""File inspection and metadata functions."""

from __future__ import annotations

from collections import Counter
from os import PathLike, fspath

from . import _core  # type: ignore[attr-defined]
from .types import Compression, FrameFileInfo, FrameInfo


def get_channels(filename: str | PathLike[str]) -> list[str]:
    """
    Get a list of all channels in a GWF file.

    Parameters
    ----------
    filename : str or path-like
        Path to the GWF file

    Returns
    -------
    channels : list[str]
        List of all channel names

    Examples
    --------
    >>> channels = gwframe.get_channels('data.gwf')
    >>> print(f"Found {len(channels)} channels")
    >>> for channel in channels:
    ...     print(channel)
    """
    stream = _core.IFrameFStream(fspath(filename))
    toc = stream.get_toc()
    return [*toc.get_adc(), *toc.get_proc(), *toc.get_sim()]


def _detect_compression(stream: _core.IFrameFStream, toc: _core.FrTOC) -> int:
    """
    Detect file-level compression scheme from available channels.

    Compression is set at the stream level when writing frames, so all channels
    should use the same compression scheme. However, very small data arrays may
    be left uncompressed (RAW) even when compression is specified, as the
    compression overhead would exceed any space savings. This function samples
    multiple channels and prefers non-RAW schemes to identify the intended
    file-level compression that should be used when writing similar files.

    Parameters
    ----------
    stream : IFrameFStream
        Open frame file stream
    toc : FrTOC
        Table of contents for the file

    Returns
    -------
    int
        Compression scheme value (e.g., Compression.GZIP, Compression.RAW)
    """
    compression_schemes = []

    # Sample channels by type: (channel_list, read_method)
    channel_types = [
        (toc.get_proc(), stream.read_fr_proc_data),
        (toc.get_adc(), stream.read_fr_adc_data),
        (toc.get_sim(), stream.read_fr_sim_data),
    ]

    for channel_list, read_method in channel_types:
        # Sample up to 5 channels of this type
        for channel_name in channel_list[:5]:
            try:
                fr_data = read_method(0, channel_name)
                vect = fr_data.get_data_vector(0)

                # Quick check: if not compressed, it's RAW
                if not vect.is_compressed():
                    compression_schemes.append(Compression.RAW.value)
                else:
                    # Get the actual compression scheme
                    compression_schemes.append(vect.get_compression_scheme())
            except Exception:  # noqa: BLE001, S112
                # Skip channels that fail to read
                continue

    # If we found compression schemes, pick the best one
    if compression_schemes:
        # Prefer non-RAW compression (RAW might just be from small data)
        non_raw = [c for c in compression_schemes if c != Compression.RAW.value]
        if non_raw:
            # Return the most common non-RAW compression
            return Counter(non_raw).most_common(1)[0][0]
        # If everything is RAW, return RAW
        return Compression.RAW.value

    # Default to RAW if no channels found
    return Compression.RAW.value


def get_info(filename: str | PathLike[str]) -> FrameFileInfo:
    """
    Get metadata about a GWF file.

    Parameters
    ----------
    filename : str or path-like
        Path to the GWF file

    Returns
    -------
    info : FrameFileInfo
        Structured metadata containing:
        - num_frames: number of frames in file
        - channels: list of all channel names
        - frames: list of FrameInfo objects with complete frame metadata

    Examples
    --------
    >>> info = gwframe.get_info('data.gwf')
    >>> print(f"File contains {info.num_frames} frames")
    >>> print(f"Frame 0: {info.frames[0].name} at GPS {info.frames[0].t0}")
    >>> print(f"Channels: {', '.join(info.channels)}")
    """
    stream = _core.IFrameFStream(fspath(filename))
    num_frames = stream.get_number_of_frames()
    toc = stream.get_toc()

    # Get all channels
    channels = [*toc.get_adc(), *toc.get_proc(), *toc.get_sim()]

    # Detect compression from first available channel in first frame
    compression = _detect_compression(stream, toc)

    # Read each frame header to get complete metadata
    frames = []
    for i in range(num_frames):
        # Read frame header
        frame_h = stream.read_frame_n(i)

        # Extract metadata from frame header
        time = frame_h.get_gps_time()
        t0 = float(time.sec) + float(time.nsec) * 1e-9

        frames.append(
            FrameInfo(
                index=i,
                t0=t0,
                duration=frame_h.get_dt(),
                name=frame_h.get_name(),
                run=frame_h.get_run(),
                frame_number=frame_h.get_frame(),
            )
        )

    return FrameFileInfo(
        num_frames=num_frames,
        channels=channels,
        frames=frames,
        compression=compression,
    )
