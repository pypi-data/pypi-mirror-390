# Copyright (c) 2025, California Institute of Technology and contributors
#
# You should have received a copy of the licensing terms for this
# software included in the file "LICENSE" located in the top-level
# directory of this package. If you did not, you can view a copy at
# https://git.ligo.org/patrick.godwin/gwframe/-/raw/main/LICENSE

"""Write functions and Frame class for GWF files."""

from __future__ import annotations

from collections.abc import MutableMapping
from os import PathLike, fspath

import numpy as np
import numpy.typing as npt

from . import _core  # type: ignore[attr-defined]
from .types import Compression, DetectorLocation, TimeSeries

_DTYPE_TO_FRVECT = {
    np.dtype("float64"): _core.FrVect.FR_VECT_8R,
    np.dtype("float32"): _core.FrVect.FR_VECT_4R,
    np.dtype("int32"): _core.FrVect.FR_VECT_4S,
    np.dtype("int16"): _core.FrVect.FR_VECT_2S,
    np.dtype("int64"): _core.FrVect.FR_VECT_8S,
    np.dtype("uint8"): _core.FrVect.FR_VECT_1U,
    np.dtype("uint16"): _core.FrVect.FR_VECT_2U,
    np.dtype("uint32"): _core.FrVect.FR_VECT_4U,
    np.dtype("uint64"): _core.FrVect.FR_VECT_8U,
    np.dtype("complex64"): _core.FrVect.FR_VECT_8C,
    np.dtype("complex128"): _core.FrVect.FR_VECT_16C,
}


class FrameWriter:
    """
    Context manager for writing multiple frames to a single GWF file.

    This is the recommended way to write multiple frames to a file, as it
    keeps the output stream open and efficiently writes frames sequentially.

    Parameters
    ----------
    filename : str or path-like
        Output file path
    compression : int, optional
        Compression scheme (default: Compression.ZERO_SUPPRESS_OTHERWISE_GZIP)
    compression_level : int, optional
        Compression level 0-9 (default: 6)

    Examples
    --------
    >>> # Write multiple 1-second frames
    >>> with gwframe.FrameWriter('output.gwf') as writer:
    ...     for i in range(10):
    ...         t0 = 1234567890.0 + i
    ...         data = np.random.randn(16384)
    ...         writer.write(data, t0=t0, dt=1.0/16384, name='L1:TEST')

    >>> # Write Frame objects directly
    >>> with gwframe.FrameWriter('output.gwf') as writer:
    ...     for i in range(10):
    ...         frame = gwframe.Frame(t0=1234567890.0 + i, duration=1.0, name='L1')
    ...         frame.add_channel('L1:TEST', data[i], dt=1.0/16384)
    ...         writer.write_frame(frame)
    """

    __slots__ = (
        "_frame_number",
        "_stream",
        "compression",
        "compression_level",
        "filename",
    )

    def __init__(
        self,
        filename: str | PathLike[str],
        compression: int = Compression.ZERO_SUPPRESS_OTHERWISE_GZIP,
        compression_level: int = 6,
        frame_number: int = 0,
    ):
        self.filename = fspath(filename)
        self.compression = compression
        self.compression_level = compression_level
        self._stream = None
        self._frame_number = frame_number  # Track and auto-increment

    def __enter__(self):
        self._stream = _core.OFrameFStream(self.filename)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Stream will be closed automatically when it goes out of scope
        self._stream = None
        return False

    def write_frame(self, frame: Frame):
        """
        Write a Frame object to the file.

        Parameters
        ----------
        frame : Frame
            The frame to write

        Examples
        --------
        >>> with gwframe.FrameWriter('output.gwf') as writer:
        ...     frame = gwframe.Frame(t0=1234567890.0, duration=1.0, name='L1')
        ...     frame.add_channel('L1:TEST', data, dt=1.0/16384)
        ...     writer.write_frame(frame)

        Notes
        -----
        If the frame was created with frame_number=0 (default), the writer
        will use its tracked frame_number. Otherwise, the frame's frame_number
        is used. Frame numbers auto-increment with each write.
        """
        if self._stream is None:
            msg = "FrameWriter not opened (use 'with' statement)"
            raise RuntimeError(msg)

        frame.write_to_stream(self._stream, self.compression, self.compression_level)

        # Auto-increment for next frame
        self._frame_number += 1

    def write(
        self,
        channels: dict[str, npt.NDArray] | npt.NDArray,
        t0: float,
        sample_rate: float | dict[str, float],
        *,
        name: str = "",
        run: int = 0,
        unit: str | dict[str, str] = "",
        channel_type: str = "proc",
    ):
        """
        Convenience method to write data directly without creating Frame object.

        This creates a Frame internally and writes it immediately.

        Parameters
        ----------
        channels : dict or np.ndarray
            Channel data. Either:
            - dict mapping channel names to 1D NumPy arrays
            - Single 1D NumPy array (requires channel name in name parameter)
        t0 : float
            GPS start time of the frame
        sample_rate : float or dict
            Sample rate in Hz. Either:
            - Single float value used for all channels
            - dict mapping channel names to sample rates
        name : str, optional
            Frame name (e.g., 'L1') or single channel name if channels is an array
        run : int, optional
            Run number (default: 0, negative for simulated data)
        unit : str or dict, optional
            Physical unit. Either:
            - Single string used for all channels (default: '')
            - dict mapping channel names to units
        channel_type : str, optional
            Type of channels: 'proc' (processed, default) or 'sim' (simulated)

        Examples
        --------
        >>> with gwframe.FrameWriter('output.gwf') as writer:
        ...     for i in range(10):
        ...         data = np.random.randn(16384)
        ...         writer.write(
        ...             data, t0=1234567890.0 + i, sample_rate=16384, name='L1:TEST'
        ...         )
        """
        if self._stream is None:
            msg = "FrameWriter not opened (use 'with' statement)"
            raise RuntimeError(msg)

        # Handle single array case - convert to dict
        if isinstance(channels, np.ndarray):
            if not name:
                msg = "name parameter required when channels is a single array"
                raise ValueError(msg)
            channel_name = name
            channels = {channel_name: channels}
            frame_name = channel_name.split(":")[0] if ":" in channel_name else ""
        else:
            frame_name = name

        # Determine frame duration from first channel
        first_channel = next(iter(channels.keys()))
        first_data = channels[first_channel]
        first_rate = (
            sample_rate
            if isinstance(sample_rate, (int, float))
            else sample_rate[first_channel]
        )
        duration = len(first_data) / first_rate

        # Create frame with auto-incremented frame number
        frame = Frame(
            t0=t0,
            duration=duration,
            name=frame_name,
            run=run,
            frame_number=self._frame_number,
        )

        # Add all channels to the frame
        _populate_frame_with_channels(frame, channels, sample_rate, unit, channel_type)

        # Write the frame (this will auto-increment _frame_number)
        self.write_frame(frame)


class Frame(MutableMapping):
    """
    High-level interface for creating and manipulating GWF frames.

    This class provides a Pythonic interface to the underlying frameCPP
    FrameH class, with simplified methods for adding data and metadata.

    Parameters
    ----------
    t0 : float
        GPS start time of the frame
    duration : float
        Duration of the frame in seconds
    name : str, optional
        Frame name (e.g., 'L1' for LIGO Livingston)
    run : int, optional
        Run number (default: 0, negative for simulated data)

    Notes
    -----
    Detector information is automatically added to the frame based on
    channel names. When you add a channel with a name like 'L1:TEST',
    the detector information for L1 will be automatically included.

    Examples
    --------
    >>> frame = gwframe.Frame(t0=1234567890.0, duration=1.0, name='L1', run=1)
    >>> frame.add_channel('L1:TEST', data=np.random.randn(16384),
    ...                   dt=1.0/16384, unit='counts')
    >>> frame.write('output.gwf')
    """

    __slots__ = (
        "_channels",
        "_channels_modified",
        "_detectors_added",
        "_frame",
        "_frdatas",
        "_gps_time",
        "_t0",
        "_vects",
        "duration",
        "frame_number",
        "name",
        "run",
    )

    def __init__(
        self,
        t0: float,
        duration: float,
        name: str = "",
        run: int = 0,
        frame_number: int = 0,
    ):
        # Convert GPS time
        self._gps_time = _core.gpstime_from_float(t0)

        # Get leap seconds from GPS time (TAI-UTC offset)
        leap_seconds = self._gps_time.get_leap_seconds()

        # Use full constructor with frame_number and leap_seconds
        self._frame = _core.FrameH(
            name, run, frame_number, self._gps_time, leap_seconds, duration
        )

        # Store for convenience
        self._t0 = t0
        self.duration = duration
        self.name = name
        self.run = run
        self.frame_number = frame_number

        # Keep references to vects to prevent premature garbage collection
        # (C++ frame holds raw pointers, so Python must keep objects alive)
        self._vects: list[_core.FrVect] = []
        self._frdatas: list[_core.FrProcData | _core.FrSimData] = []

        # Track which detectors we've added to avoid duplicates
        self._detectors_added: set[str] = set()

        # Store channels for dict-like access
        self._channels: dict[str, TimeSeries] = {}

        # Track if channels were modified via dict interface
        self._channels_modified = False

    @property
    def t0(self) -> float:
        """GPS start time of the frame."""
        return self._t0

    @t0.setter
    def t0(self, value: float):
        """Set GPS start time of the frame."""
        self._t0 = value
        self._gps_time = _core.gpstime_from_float(value)

    @property
    def _handle(self):
        """Access to underlying FrameH object."""
        return self._frame

    def add_history(self, name: str, comment: str, time: int | None = None):
        """
        Add a history/metadata entry to the frame.

        Parameters
        ----------
        name : str
            Name/key for this metadata entry
        comment : str
            The metadata value/comment
        time : int, optional
            GPS time for this entry (default: frame start time)
        """
        if time is None:
            time = int(self.t0)
        history = _core.FrHistory(name, time, comment)
        self._frame.append_frhistory(history)

    def add_channel(
        self,
        channel: str,
        data: npt.NDArray,
        sample_rate: float,
        unit: str = "",
        comment: str = "",
        channel_type: str = "proc",
    ):
        """
        Add a data channel to this frame.

        Parameters
        ----------
        channel : str
            Channel name (e.g., 'L1:TEST-CHANNEL')
        data : np.ndarray
            1D NumPy array containing the channel data
        sample_rate : float
            Sample rate in Hz (samples per second)
        unit : str, optional
            Physical unit of the data (e.g., 'strain', 'counts')
        comment : str, optional
            Comment or description for this channel
        channel_type : str, optional
            Type of channel: 'proc' (processed, default) or 'sim' (simulated)

        Examples
        --------
        >>> frame.add_channel('L1:TEST', data=np.random.randn(16384),
        ...                   sample_rate=16384, unit='counts')

        Notes
        -----
        The data type (float64, float32, int32, etc.) is automatically
        determined from the NumPy array dtype.
        """
        # Ensure data is a 1D numpy array
        if data.ndim != 1:
            msg = f"Data must be 1D array, got shape {data.shape}"
            raise ValueError(msg)

        # Extract detector prefix from channel name (e.g., 'L1:TEST' -> 'L1')
        # and add detector information if it's a known detector
        if ":" in channel:
            prefix = channel.split(":", 1)[0]
            if prefix not in self._detectors_added:
                try:
                    # Check if this is a valid detector
                    detector_loc = DetectorLocation[prefix]
                    # Get detector info for this location and GPS time
                    detector = _core.get_detector(detector_loc, self._gps_time)
                    # Append to frame based on channel type
                    if channel_type == "sim":
                        self._frame.append_fr_detector_sim(detector)
                    else:  # 'proc' or 'adc'
                        self._frame.append_fr_detector_proc(detector)
                    # Mark this detector as added
                    self._detectors_added.add(prefix)
                except KeyError:
                    # Not a known detector prefix, that's okay
                    pass

        n_samples = len(data)

        # Convert sample_rate to dt (sample spacing)
        dt = 1.0 / sample_rate

        if data.dtype not in _DTYPE_TO_FRVECT:
            msg = (
                f"Unsupported data type: {data.dtype}. "
                f"Supported types: {list(_DTYPE_TO_FRVECT.keys())}"
            )
            raise ValueError(msg)

        frvect_type = _DTYPE_TO_FRVECT[data.dtype]

        # Create dimension
        dim = _core.Dimension(n_samples, dt, "s", 0.0)

        # Create FrVect and populate with data
        vect = _core.FrVect(channel, frvect_type, 1, dim, unit)
        # Direct C++ memcpy ~50% faster than get_data_array()[:] = data
        vect.set_data(data)

        # Create appropriate Fr*Data container and add to frame
        if channel_type == "proc":
            # Calculate Nyquist frequency (frange) from sample rate
            frange = sample_rate / 2.0  # Nyquist frequency

            # FrProcData: name, comment, type, subtype, time_offset, trange,
            # fshift, phase, frange, bandwidth
            frdata = _core.FrProcData(
                channel, comment, 1, 0, 0.0, self.duration, 0.0, 0.0, frange, 0.0
            )
            frdata.append_data(vect)
            self._frame.append_fr_proc_data(frdata)
        elif channel_type == "sim":
            # FrSimData: name, comment, sample_rate, time_offset, fshift, phase
            frdata = _core.FrSimData(channel, comment, sample_rate, 0.0, 0.0, 0.0)
            frdata.append_data(vect)
            self._frame.append_fr_sim_data(frdata)
        else:
            # FIXME: ADC channel support needs to be implemented
            # Requires proper GetRawData()/SetRawData() initialization in C++ bindings
            msg = (
                f"Unsupported channel_type: {channel_type}. "
                f"Supported types: 'proc', 'sim'"
            )
            raise ValueError(msg)

        # Keep references alive to prevent garbage collection
        # (C++ uses raw pointers with empty deleters, so Python must keep objects alive)
        self._vects.append(vect)
        self._frdatas.append(frdata)

        # Also store in channels dict for dict-like access
        self._channels[channel] = TimeSeries(
            array=data,
            name=channel,
            dtype=vect.get_type(),
            t0=self.t0,
            dt=dt,
            duration=len(data) * dt,
            sample_rate=sample_rate,
            unit=unit,
            type=channel_type,
        )

    def write_to_stream(
        self,
        stream,
        compression: int = Compression.ZERO_SUPPRESS_OTHERWISE_GZIP,
        compression_level: int = 6,
    ):
        """
        Write this frame to an output stream.

        This is used internally by FrameWriter for writing multiple frames.

        Parameters
        ----------
        stream : OFrameFStream
            Output stream to write to
        compression : int, optional
            Compression scheme (default: Compression.ZERO_SUPPRESS_OTHERWISE_GZIP)
        compression_level : int, optional
            Compression level 0-9 (default: 6)
        """
        # Rebuild frame if channels were modified via dict interface
        if self._channels_modified:
            self._rebuild_frame()

        self._frame.write(stream, compression, compression_level)

    def write(
        self,
        filename: str | PathLike[str],
        compression: int = Compression.ZERO_SUPPRESS_OTHERWISE_GZIP,
        compression_level: int = 6,
    ):
        """
        Write this frame to a GWF file.

        Parameters
        ----------
        filename : str or path-like
            Output file path
        compression : int, optional
            Compression scheme (default: Compression.ZERO_SUPPRESS_OTHERWISE_GZIP)
            Use Compression.RAW for no compression
        compression_level : int, optional
            Compression level 0-9 (default: 6, higher = more compression)

        Examples
        --------
        >>> frame.write('output.gwf')
        >>> frame.write('output_raw.gwf', compression=gwframe.Compression.RAW)
        """
        # Rebuild frame if channels were modified via dict interface
        if self._channels_modified:
            self._rebuild_frame()

        # Create output stream inline (ensures proper flushing)
        self._frame.write(
            _core.OFrameFStream(fspath(filename)), compression, compression_level
        )

    def __repr__(self):
        return (
            f"<Frame name='{self.name}' t0={self.t0:.6f} "
            f"duration={self.duration} run={self.run}>"
        )

    def __getitem__(self, key: str) -> TimeSeries:
        """Get channel by name."""
        return self._channels[key]

    def __setitem__(self, key: str, value: TimeSeries) -> None:
        """Set/update channel with TimeSeries."""
        self._channels[key] = value
        self._channels_modified = True

    def __delitem__(self, key: str) -> None:
        """Delete channel by name. Frame will be rebuilt on write."""
        del self._channels[key]
        self._channels_modified = True

    def __iter__(self):
        """Iterate over channel names."""
        return iter(self._channels)

    def __len__(self) -> int:
        """Return number of channels."""
        return len(self._channels)

    def _rebuild_frame(self):
        """Rebuild internal frame from _channels dict."""
        # Create fresh FrameH
        self._frame = _core.FrameH(
            self.name,
            self.run,
            self.frame_number,
            self._gps_time,
            self._gps_time.get_leap_seconds(),
            self.duration,
        )

        # Clear internal lists
        self._vects = []
        self._frdatas = []
        self._detectors_added = set()

        # Re-add all channels from _channels dict
        for channel_name, ts in self._channels.items():
            self.add_channel(
                channel_name,
                ts.array,
                ts.sample_rate,
                unit=ts.unit,
                channel_type=ts.type,
            )

        # Reset modified flag after rebuild
        self._channels_modified = False


def _populate_frame_with_channels(
    frame: Frame,
    channels: dict[str, npt.NDArray],
    sample_rate: float | dict[str, float],
    unit: str | dict[str, str],
    channel_type: str,
) -> None:
    """
    Populate a Frame with multiple channels.

    Helper function to add multiple channels to a frame, handling
    both scalar and per-channel sample rates and units.

    Parameters
    ----------
    frame : Frame
        Frame object to populate
    channels : dict
        Dictionary mapping channel names to data arrays
    sample_rate : float or dict
        Sample rate(s) in Hz
    unit : str or dict
        Physical unit(s)
    channel_type : str
        Type of channels ('proc' or 'sim')
    """
    # Get first channel's sample rate as fallback
    first_channel = next(iter(channels.keys()))
    first_rate = (
        sample_rate
        if isinstance(sample_rate, (int, float))
        else sample_rate[first_channel]
    )

    # Hoist type checks out of loop for performance
    sample_rate_is_scalar = isinstance(sample_rate, (int, float))
    unit_is_str = isinstance(unit, str)

    # Add each channel
    for channel_name, data in channels.items():
        # Get sample_rate for this channel
        channel_rate: float
        if sample_rate_is_scalar:
            channel_rate = sample_rate  # type: ignore[assignment]
        else:
            assert isinstance(sample_rate, dict)
            channel_rate = sample_rate.get(channel_name, first_rate)

        # Get unit for this channel
        channel_unit: str
        if unit_is_str:
            channel_unit = unit  # type: ignore[assignment]
        else:
            assert isinstance(unit, dict)
            channel_unit = unit.get(channel_name, "")

        # Add channel
        frame.add_channel(
            channel_name,
            data,
            channel_rate,
            unit=channel_unit,
            channel_type=channel_type,
        )


def write(
    filename: str | PathLike[str],
    channels: dict[str, npt.NDArray] | npt.NDArray,
    t0: float,
    sample_rate: float | dict[str, float],
    *,
    name: str = "",
    run: int = 0,
    unit: str | dict[str, str] = "",
    channel_type: str = "proc",
    compression: int = Compression.ZERO_SUPPRESS_OTHERWISE_GZIP,
    compression_level: int = 6,
):
    """
    Write channel data to a GWF file.

    This is a convenience function for simple write operations. For more
    control, use the Frame class directly.

    Parameters
    ----------
    filename : str or path-like
        Output file path
    channels : dict or np.ndarray
        Channel data. Either:
        - dict mapping channel names to 1D NumPy arrays
        - Single 1D NumPy array (requires channel name in name parameter)
    t0 : float
        GPS start time of the frame
    sample_rate : float or dict
        Sample rate in Hz. Either:
        - Single float value used for all channels
        - dict mapping channel names to sample rates
    name : str, optional
        Frame name (e.g., 'L1') or single channel name if channels is an array
    run : int, optional
        Run number (default: 0, negative for simulated data)
    unit : str or dict, optional
        Physical unit. Either:
        - Single string used for all channels (default: '')
        - dict mapping channel names to units
    channel_type : str, optional
        Type of channels: 'proc' (processed, default) or 'sim' (simulated)
    compression : int, optional
        Compression scheme (default: Compression.ZERO_SUPPRESS_OTHERWISE_GZIP)
    compression_level : int, optional
        Compression level 0-9 (default: 6)

    Examples
    --------
    >>> # Write single channel
    >>> data = np.sin(np.linspace(0, 2*np.pi, 16384))
    >>> gwframe.write('output.gwf', data, t0=1234567890.0, sample_rate=16384,
    ...               name='L1:TEST', unit='strain')

    >>> # Write multiple channels
    >>> gwframe.write('output.gwf',
    ...               channels={'L1:CHAN1': data1, 'L1:CHAN2': data2},
    ...               t0=1234567890.0, sample_rate=16384, name='L1')

    >>> # Write with different sample rates
    >>> gwframe.write('output.gwf',
    ...               channels={'L1:FAST': data1, 'L1:SLOW': data2},
    ...               t0=1234567890.0,
    ...               sample_rate={'L1:FAST': 16384, 'L1:SLOW': 256},
    ...               name='L1')

    See Also
    --------
    Frame : For more control over frame creation and metadata
    """
    # Handle single array case - convert to dict
    if isinstance(channels, np.ndarray):
        if not name:
            msg = "name parameter required when channels is a single array"
            raise ValueError(msg)
        # Use name as the channel name
        channel_name = name
        channels = {channel_name: channels}
        # Set frame name to empty or first part before colon
        frame_name = channel_name.split(":")[0] if ":" in channel_name else ""
    else:
        frame_name = name

    # Determine frame duration from first channel
    first_channel = next(iter(channels.keys()))
    first_data = channels[first_channel]
    first_rate = (
        sample_rate
        if isinstance(sample_rate, (int, float))
        else sample_rate[first_channel]
    )
    duration = len(first_data) / first_rate

    # Create frame
    frame = Frame(t0=t0, duration=duration, name=frame_name, run=run)

    # Add all channels to the frame
    _populate_frame_with_channels(frame, channels, sample_rate, unit, channel_type)

    # Write frame
    frame.write(filename, compression=compression, compression_level=compression_level)
