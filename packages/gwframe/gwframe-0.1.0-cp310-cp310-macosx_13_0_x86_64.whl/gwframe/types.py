# Copyright (c) 2025, California Institute of Technology and contributors
#
# You should have received a copy of the licensing terms for this
# software included in the file "LICENSE" located in the top-level
# directory of this package. If you did not, you can view a copy at
# https://git.ligo.org/patrick.godwin/gwframe/-/raw/main/LICENSE

"""Data types and constants for gwframe."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import TYPE_CHECKING

from . import _core  # type: ignore[attr-defined]

if TYPE_CHECKING:
    import numpy as np
    import numpy.typing as npt


class DetectorLocation(IntEnum):
    """
    Detector location identifiers for GWF files.

    These constants identify specific gravitational wave detectors
    and are used with the GetDetector function.

    - G1: GEO600 (Germany)
    - H1: LIGO Hanford 4km (USA)
    - H2: LIGO Hanford 2km (USA, decommissioned)
    - K1: KAGRA (Japan)
    - L1: LIGO Livingston 4km (USA)
    - T1: TAMA300 (Japan, decommissioned)
    - V1: Virgo (Italy)
    """

    G1 = _core.DETECTOR_LOCATION_G1  # GEO600
    H1 = _core.DETECTOR_LOCATION_H1  # LIGO Hanford 4km
    H2 = _core.DETECTOR_LOCATION_H2  # LIGO Hanford 2km (decommissioned)
    K1 = _core.DETECTOR_LOCATION_K1  # KAGRA
    L1 = _core.DETECTOR_LOCATION_L1  # LIGO Livingston 4km
    T1 = _core.DETECTOR_LOCATION_T1  # TAMA300 (decommissioned)
    V1 = _core.DETECTOR_LOCATION_V1  # Virgo


class ChannelType(str, Enum):
    """
    Channel data types in GWF files.

    - PROC: Processed data (FrProcData)
    - ADC: Raw ADC data (FrAdcData)
    - SIM: Simulated data (FrSimData)
    """

    PROC = "proc"
    ADC = "adc"
    SIM = "sim"


class Compression(IntEnum):
    """
    Compression schemes for GWF files.

    See LIGO-T970130 for details on compression algorithms.

    Standard modes:
    - RAW: No compression
    - GZIP: Standard GZIP compression
    - DIFF_GZIP: Differentiate data then apply GZIP
    - ZERO_SUPPRESS_WORD_2: Zero-suppress 2-byte (16-bit) words
    - ZERO_SUPPRESS_WORD_4: Zero-suppress 4-byte (32-bit) words
    - ZERO_SUPPRESS_WORD_8: Zero-suppress 8-byte (64-bit) words

    Meta modes (adaptive):
    - ZERO_SUPPRESS_OTHERWISE_GZIP: Zero-suppress integers, GZIP floats (recommended)
    - BEST_COMPRESSION: Try all modes, use best compression ratio

    Aliases:
    - ZERO_SUPPRESS_SHORT: Alias for ZERO_SUPPRESS_WORD_2
    - ZERO_SUPPRESS_INT_FLOAT: Alias for ZERO_SUPPRESS_WORD_4
    """

    # Standard compression modes
    RAW = _core.FrVect.RAW
    GZIP = _core.FrVect.GZIP
    DIFF_GZIP = _core.FrVect.DIFF_GZIP
    ZERO_SUPPRESS_WORD_2 = _core.FrVect.ZERO_SUPPRESS_WORD_2
    ZERO_SUPPRESS_WORD_4 = _core.FrVect.ZERO_SUPPRESS_WORD_4
    ZERO_SUPPRESS_WORD_8 = _core.FrVect.ZERO_SUPPRESS_WORD_8

    # Meta compression modes (adaptive)
    ZERO_SUPPRESS_OTHERWISE_GZIP = _core.FrVect.ZERO_SUPPRESS_OTHERWISE_GZIP
    BEST_COMPRESSION = _core.FrVect.BEST_COMPRESSION

    # Backward compatibility aliases
    ZERO_SUPPRESS_SHORT = _core.FrVect.ZERO_SUPPRESS_SHORT
    ZERO_SUPPRESS_INT_FLOAT = _core.FrVect.ZERO_SUPPRESS_INT_FLOAT


class FrVectType(IntEnum):
    """
    Data types for FrVect arrays.

    Provides human-readable aliases for frameCPP data type constants.
    """

    # Floating point types
    FLOAT64 = _core.FrVect.FR_VECT_8R  # double precision
    FLOAT32 = _core.FrVect.FR_VECT_4R  # single precision

    # Signed integer types
    INT64 = _core.FrVect.FR_VECT_8S
    INT32 = _core.FrVect.FR_VECT_4S
    INT16 = _core.FrVect.FR_VECT_2S

    # Unsigned integer types
    UINT64 = _core.FrVect.FR_VECT_8U
    UINT32 = _core.FrVect.FR_VECT_4U
    UINT16 = _core.FrVect.FR_VECT_2U
    UINT8 = _core.FrVect.FR_VECT_1U

    # Legacy aliases for compatibility
    FR_VECT_8R = _core.FrVect.FR_VECT_8R  # double
    FR_VECT_4R = _core.FrVect.FR_VECT_4R  # float
    FR_VECT_4S = _core.FrVect.FR_VECT_4S  # int32
    FR_VECT_2S = _core.FrVect.FR_VECT_2S  # int16
    FR_VECT_8S = _core.FrVect.FR_VECT_8S  # int64
    FR_VECT_1U = _core.FrVect.FR_VECT_1U  # uint8
    FR_VECT_2U = _core.FrVect.FR_VECT_2U  # uint16
    FR_VECT_4U = _core.FrVect.FR_VECT_4U  # uint32
    FR_VECT_8U = _core.FrVect.FR_VECT_8U  # uint64


class FrProcDataType(IntEnum):
    """
    Type classification for FrProcData structures.

    Indicates the dimensionality and structure of processed data.
    """

    UNKNOWN = _core.FrProcData.UNKNOWN_TYPE
    TIME_SERIES = _core.FrProcData.TIME_SERIES
    FREQUENCY_SERIES = _core.FrProcData.FREQUENCY_SERIES
    OTHER_1D_SERIES_DATA = _core.FrProcData.OTHER_1D_SERIES_DATA
    TIME_FREQUENCY = _core.FrProcData.TIME_FREQUENCY
    WAVELETS = _core.FrProcData.WAVELETS
    MULTI_DIMENSIONAL = _core.FrProcData.MULTI_DIMENSIONAL


class FrProcDataSubType(IntEnum):
    """
    Subtype classification for FrProcData structures.

    Provides detailed information about the data processing or analysis type.
    """

    UNKNOWN = _core.FrProcData.UNKNOWN_SUB_TYPE
    DFT = _core.FrProcData.DFT
    AMPLITUDE_SPECTRAL_DENSITY = _core.FrProcData.AMPLITUDE_SPECTRAL_DENSITY
    POWER_SPECTRAL_DENSITY = _core.FrProcData.POWER_SPECTRAL_DENSITY
    CROSS_SPECTRAL_DENSITY = _core.FrProcData.CROSS_SPECTRAL_DENSITY
    COHERENCE = _core.FrProcData.COHERENCE
    TRANSFER_FUNCTION = _core.FrProcData.TRANSFER_FUNCTION


@dataclass(slots=True, frozen=True)
class FrameInfo:
    """
    Metadata about a single frame in a GWF file.

    This dataclass holds metadata for a frame without the actual channel data.

    Attributes
    ----------
    index : int
        Frame index in the file (0-based)
    t0 : float
        Start time in GPS seconds
    duration : float
        Frame duration in seconds
    name : str
        Frame name (e.g., 'H1', 'L1')
    run : int
        Run number (negative for simulated data)
    frame_number : int
        Frame sequence number

    Examples
    --------
    >>> info = gwframe.get_info('data.gwf')
    >>> frame = info.frames[0]
    >>> print(f"Frame {frame.index}: {frame.name} at GPS {frame.t0}")
    """

    index: int
    t0: float
    duration: float
    name: str
    run: int
    frame_number: int


@dataclass(slots=True, frozen=True)
class FrameFileInfo:
    """
    Complete metadata about a GWF file.

    This dataclass holds file-level and frame-level metadata for a GWF file.

    Attributes
    ----------
    num_frames : int
        Total number of frames in the file
    channels : list[str]
        List of all channel names in the file
    frames : list[FrameInfo]
        List of metadata for each frame
    compression : int
        Compression scheme used for all channels in the file (e.g., Compression.GZIP)

    Examples
    --------
    >>> info = gwframe.get_info('data.gwf')
    >>> print(f"File contains {info.num_frames} frames")
    >>> print(f"Channels: {', '.join(info.channels)}")
    >>> print(f"Compression: {Compression(info.compression).name}")
    >>> # Preserve compression when writing
    >>> with FrameWriter('output.gwf', **info.compression_settings) as writer:
    ...     pass
    """

    num_frames: int
    channels: list[str]
    frames: list[FrameInfo]
    compression: int

    @property
    def compression_settings(self) -> dict[str, int]:
        """
        Return compression settings as kwargs for FrameWriter.

        Returns
        -------
        dict[str, int]
            Compression settings suitable for FrameWriter constructor

        Examples
        --------
        >>> info = gwframe.get_info('input.gwf')
        >>> with gwframe.FrameWriter(
        ...     'output.gwf', **info.compression_settings
        ... ) as writer:
        ...     # Frames written with same compression as input file
        ...     pass
        """
        return {"compression": self.compression}


@dataclass(slots=True, frozen=True)
class TimeSeries:
    """
    Time series data from a GWF channel.

    This dataclass holds the array data and metadata for a channel read from
    a GWF file.

    Attributes
    ----------
    array : np.ndarray
        NumPy array containing the time series data
    name : str
        Channel name (e.g., 'H1:LOSC-STRAIN')
    dtype : int
        frameCPP data type code (e.g., FR_VECT_8R for double)
    t0 : float
        Start time in GPS seconds
    dt : float
        Sample spacing in seconds
    duration : float
        Total duration in seconds
    sample_rate : float
        Sampling rate in Hz (1/dt)
    unit : str
        Physical unit of the data (e.g., 'strain')
    type : str
        Channel type: 'proc' (processed), 'adc' (raw ADC), or 'sim' (simulated)

    Examples
    --------
    >>> data = gwframe.read('data.gwf', 'H1:LOSC-STRAIN')
    >>> print(f"Channel: {data.name}")
    >>> print(f"Duration: {data.duration} s at {data.sample_rate} Hz")
    >>> print(f"Data shape: {data.array.shape}")
    """

    array: npt.NDArray[np.floating]
    name: str
    dtype: int
    t0: float
    dt: float
    duration: float
    sample_rate: float
    unit: str
    type: str
