"""
Basic tests for gwframe package
"""

import pytest


def test_import():
    """Test that the package can be imported"""
    import gwframe

    assert gwframe is not None


def test_version():
    """Test that version is accessible"""
    import gwframe

    assert hasattr(gwframe, "__version__")
    assert isinstance(gwframe.__version__, str)


def test_api_exports():
    """Test that expected API functions are exported"""
    import gwframe

    # Core API
    assert hasattr(gwframe, "read")
    assert hasattr(gwframe, "write")
    assert hasattr(gwframe, "get_channels")
    assert hasattr(gwframe, "get_info")
    assert hasattr(gwframe, "Frame")
    assert hasattr(gwframe, "FrameWriter")

    # Types
    assert hasattr(gwframe, "TimeSeries")
    assert hasattr(gwframe, "Compression")
    assert hasattr(gwframe, "FrVectType")


def test_frame_creation():
    """Test creating a Frame object"""
    import gwframe

    frame = gwframe.Frame(t0=1234567890.0, duration=1.0, name="L1", run=1)

    assert frame.t0 == 1234567890.0
    assert frame.duration == 1.0
    assert frame.name == "L1"
    assert frame.run == 1

    # Check repr
    repr_str = repr(frame)
    assert "Frame" in repr_str
    assert "L1" in repr_str


def test_frame_add_history():
    """Test adding history/metadata to a frame"""
    import gwframe

    frame = gwframe.Frame(t0=1234567890.0, duration=1.0, name="L1")
    frame.add_history("TEST_KEY", "test_value")


def test_gpstime():
    """Test GPSTime handling"""
    import gwframe._core as core

    # Create GPSTime from seconds and nanoseconds
    gps = core.GPSTime(1234567890, 500000000)
    assert gps.sec == 1234567890
    assert gps.nsec == 500000000

    # Convert to float
    gps_float = gps.to_float()
    assert abs(gps_float - 1234567890.5) < 1e-9

    # Convert to tuple
    gps_tuple = gps.to_tuple()
    assert gps_tuple == (1234567890, 500000000)

    # Create from float
    gps2 = core.gpstime_from_float(1234567890.5)
    assert abs(gps2.to_float() - 1234567890.5) < 1e-6


def test_compression_enum():
    """Test that Compression enum is available"""
    import gwframe

    # Check compression enum values exist
    assert hasattr(gwframe.Compression, "RAW")
    assert hasattr(gwframe.Compression, "GZIP")
    assert hasattr(gwframe.Compression, "ZERO_SUPPRESS_OTHERWISE_GZIP")


def test_read_requires_valid_file():
    """Test that reading a non-existent file raises an error"""
    import gwframe

    with pytest.raises(RuntimeError):
        gwframe.read("/nonexistent/file.gwf", "L1:STRAIN")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
