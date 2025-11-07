"""Pytest configuration and fixtures for gwframe tests."""

import os
from pathlib import Path

import pytest


@pytest.fixture
def test_data_dir():
    """Return path to test data directory.

    Checks GWFRAME_TEST_DATA_DIR environment variable first to support
    testing installed wheels with test data from source tree.
    """
    if test_data_env := os.environ.get("GWFRAME_TEST_DATA_DIR"):
        return Path(test_data_env)
    return Path(__file__).parent / "data"


@pytest.fixture
def test_gwf_file(test_data_dir):
    """Return path to test GWF file.

    Note: This file is excluded from wheels to reduce size (4MB).
    Tests using this fixture will be skipped if the file is not present.
    """
    gwf_path = test_data_dir / "L-L1_GWOSC_16KHZ_R1-1240215487-32.gwf"
    if not gwf_path.exists():
        pytest.skip(
            "Test data file not available (excluded from wheels). "
            "Install from source or run tests on sdist to enable data-dependent tests."
        )
    return gwf_path


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "needs_data: mark test as requiring test data file (may be skipped in wheels)",
    )
