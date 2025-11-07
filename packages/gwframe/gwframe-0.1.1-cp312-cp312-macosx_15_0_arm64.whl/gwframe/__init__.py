# Copyright (c) 2025, California Institute of Technology and contributors
#
# You should have received a copy of the licensing terms for this
# software included in the file "LICENSE" located in the top-level
# directory of this package. If you did not, you can view a copy at
# https://git.ligo.org/patrick.godwin/gwframe/-/raw/main/LICENSE

from __future__ import annotations

from . import _core  # type: ignore[attr-defined]
from .errors import (
    ChannelNotFoundError,
    FrameIndexError,
    InvalidTimeRangeError,
)
from .inspect import get_channels, get_info
from .operations import (
    combine_channels,
    drop_channels,
    impute_missing_data,
    recompress_frames,
    rename_channels,
    replace_channels,
    resize_frames,
)
from .read import read, read_bytes, read_frames
from .types import (
    ChannelType,
    Compression,
    DetectorLocation,
    FrameFileInfo,
    FrameInfo,
    FrProcDataSubType,
    FrProcDataType,
    FrVectType,
    TimeSeries,
)
from .write import Frame, FrameWriter, write

# Get version from setuptools_scm
try:
    from ._version import __version__
except ImportError:
    __version__ = "0.0.0"

__all__ = [
    "ChannelNotFoundError",
    "ChannelType",
    "Compression",
    "DetectorLocation",
    "FrProcDataSubType",
    "FrProcDataType",
    "FrVectType",
    "Frame",
    "FrameFileInfo",
    "FrameIndexError",
    "FrameInfo",
    "FrameWriter",
    "InvalidTimeRangeError",
    "TimeSeries",
    "__version__",
    "combine_channels",
    "drop_channels",
    "get_channels",
    "get_info",
    "impute_missing_data",
    "read",
    "read_bytes",
    "read_frames",
    "recompress_frames",
    "rename_channels",
    "replace_channels",
    "resize_frames",
    "write",
]
