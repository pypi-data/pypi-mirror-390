"""Test complex data types (FR_VECT_8C, FR_VECT_16C) support."""

import gwframe._core as _core


def test_fr_vect_constants_exposed():
    """Test that FR_VECT_8C and FR_VECT_16C constants are exposed."""
    # Check constants exist
    fr_vect_8c = _core.FrVect.FR_VECT_8C
    fr_vect_16c = _core.FrVect.FR_VECT_16C

    # Verify they're integers
    assert isinstance(fr_vect_8c, int)
    assert isinstance(fr_vect_16c, int)

    # Verify they're different
    assert fr_vect_8c != fr_vect_16c
