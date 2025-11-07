# Copyright (c) 2025, California Institute of Technology and contributors
#
# You should have received a copy of the licensing terms for this
# software included in the file "LICENSE" located in the top-level
# directory of this package. If you did not, you can view a copy at
# https://git.ligo.org/patrick.godwin/gwframe/-/raw/main/LICENSE

"""Custom exceptions for gwframe with helpful error messages."""

from __future__ import annotations

from difflib import get_close_matches


class ChannelNotFoundError(ValueError):
    """
    Raised when one or more requested channels are not found in a GWF file.

    Provides suggestions for similar channel names and lists available channels.

    Attributes
    ----------
    channels : list[str]
        The channel name(s) that were not found
    available_channels : list[str]
        List of all available channel names in the file
    source : str or None
        Source file path or description
    """

    def __init__(
        self,
        channels: str | list[str],
        available_channels: list[str],
        source: str | None = None,
    ):
        # Normalize to list
        self.channels = [channels] if isinstance(channels, str) else list(channels)
        self.available_channels = available_channels
        self.source = source
        super().__init__(str(self))

    def __str__(self) -> str:
        """Generate helpful error message with suggestions."""
        num_missing = len(self.channels)

        # Build base error message
        if num_missing == 1:
            parts = [f"Channel '{self.channels[0]}' not found"]
        else:
            missing_str = ", ".join(self.channels)
            parts = [f"Channels not found ({num_missing}): {missing_str}"]

        if self.source:
            parts[0] += f" in '{self.source}'"
        parts[0] += "."

        # For single channel, try to find similar names
        if num_missing == 1:
            similar = get_close_matches(
                self.channels[0], self.available_channels, n=3, cutoff=0.6
            )
            if similar:
                if len(similar) == 1:
                    parts.append(f"Did you mean '{similar[0]}'?")
                else:
                    suggestions = "', '".join(similar)
                    parts.append(f"Did you mean one of: '{suggestions}'?")

        # List available channels (limit to avoid overwhelming output)
        num_channels = len(self.available_channels)
        if num_channels == 0:
            parts.append("No channels found in file.")
        elif num_channels <= 10:
            channel_list = ", ".join(self.available_channels)
            parts.append(f"Available channels ({num_channels}): {channel_list}")
        else:
            # Show first 10 channels
            channel_list = ", ".join(self.available_channels[:10])
            parts.append(
                f"Available channels ({num_channels}, showing first 10): "
                f"{channel_list}, ..."
            )

        return "\n".join(parts)


class InvalidTimeRangeError(ValueError):
    """
    Raised when requested time range does not overlap with file data.

    Attributes
    ----------
    start : float
        Requested start time (GPS seconds)
    end : float
        Requested end time (GPS seconds)
    file_start : float
        Actual start time of data in file (GPS seconds)
    file_end : float
        Actual end time of data in file (GPS seconds)
    source : str or None
        Source file path or description
    """

    def __init__(
        self,
        start: float,
        end: float,
        file_start: float,
        file_end: float,
        source: str | None = None,
    ):
        self.start = start
        self.end = end
        self.file_start = file_start
        self.file_end = file_end
        self.source = source
        super().__init__(str(self))

    def __str__(self) -> str:
        """Generate helpful error message."""
        msg = (
            f"Requested time range [{self.start}, {self.end}) does not overlap "
            f"with file range [{self.file_start}, {self.file_end})"
        )
        if self.source:
            msg += f" in '{self.source}'"
        msg += "."

        # Add specific guidance based on the issue
        if self.start >= self.file_end:
            msg += (
                f"\nRequested start time ({self.start}) is at or after "
                f"file end ({self.file_end})."
            )
        elif self.end <= self.file_start:
            msg += (
                f"\nRequested end time ({self.end}) is at or before "
                f"file start ({self.file_start})."
            )

        return msg


class FrameIndexError(IndexError):
    """
    Raised when requested frame index is out of range.

    Attributes
    ----------
    frame_index : int
        The requested frame index
    num_frames : int
        Total number of frames in the file
    source : str or None
        Source file path or description
    """

    def __init__(
        self,
        frame_index: int,
        num_frames: int,
        source: str | None = None,
    ):
        self.frame_index = frame_index
        self.num_frames = num_frames
        self.source = source
        super().__init__(str(self))

    def __str__(self) -> str:
        """Generate helpful error message."""
        max_index = self.num_frames - 1
        msg = (
            f"Frame index {self.frame_index} is out of range. "
            f"File contains {self.num_frames} frame(s) (valid indices: 0-{max_index})"
        )
        if self.source:
            msg += f" in '{self.source}'"
        msg += "."

        return msg
